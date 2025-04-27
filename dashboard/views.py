from django.contrib.auth.decorators import login_required
from django.shortcuts              import render, redirect
from decimal                       import Decimal
from .models                       import Income, Expense, Budget
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from plaid.api import plaid_api
from django.conf import settings
from .models import PlaidItem
import datetime
import json
import plaid
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
from plaid.model.country_code import CountryCode
from plaid.model.products import Products
from django.contrib.auth import logout

@login_required
def dashboard_view(request):
    if request.method == 'POST':
        if 'submit_income' in request.POST:
            amt = Decimal(request.POST.get('income_amount', '0') or '0')
            Income.objects.create(user=request.user, amount=amt)

        elif 'submit_expense' in request.POST:
            amt = Decimal(request.POST.get('expense_amount', '0') or '0')
            bid = request.POST.get('expense_budget')

            if not bid:
                from django.contrib import messages
                messages.error(request, "Please select a budget category before adding an expense.")
            else:
                try:
                    budget_obj = Budget.objects.get(id=bid, user=request.user)
                    Expense.objects.create(user=request.user,
                                           amount=amt,
                                           category=budget_obj)
                except Budget.DoesNotExist:
                    from django.contrib import messages
                    messages.error(request, "Selected budget category does not exist.")

            return redirect('dashboard')

        elif 'submit_budget' in request.POST:
            name = request.POST.get('budget_name','').strip()
            tot  = Decimal(request.POST.get('total_budget_new','0') or '0')
            if name:
                Budget.objects.create(user=request.user,
                                      name=name,
                                      total_budget=tot)
        elif 'update_budget' in request.POST:
            budget_id  = request.POST.get('budget_id')
            name = request.POST.get('budget_name', '').strip()
            tot  = Decimal(request.POST.get('total_budget_new', '0') or '0')
            try:
                budget_obj = Budget.objects.get(id=budget_id, user=request.user)
                if name:
                    budget_obj.name = name
                budget_obj.total_budget = tot
                budget_obj.save()
            except Budget.DoesNotExist:
                from django.contrib import messages
                messages.error(request, "Budget not found.")

            return redirect('dashboard')
        elif 'delete_budget' in request.POST:
            budget_id = request.POST.get('budget_id')
            try:
                Budget.objects.get(id=budget_id, user=request.user).delete()
            except Budget.DoesNotExist:
                from django.contrib import messages
                messages.error(request, "Budget not found.")
            return redirect('dashboard')

        return redirect('dashboard')

    # GET
    incomes  = Income.objects.filter(user=request.user)
    expenses = Expense.objects.filter(user=request.user)
    budgets  = Budget.objects.filter(user=request.user).order_by('id')

    total_income      = sum(i.amount for i in incomes)
    total_expenses    = sum(e.amount for e in expenses)
    remaining_balance = total_income - total_expenses

    return render(request, 'dashboard/dashboard.html', {
        'total_income':      total_income,
        'total_expenses':    total_expenses,
        'remaining_balance': remaining_balance,
        'budgets':           budgets,
    })


@login_required
def create_link_token(request):
    configuration = plaid.Configuration(
        host=plaid.Environment.Sandbox,
        api_key={
            'clientId': settings.PLAID_CLIENT_ID,
            'secret': settings.PLAID_SECRET
        }
    )
    client = get_plaid_client()

    request_data = LinkTokenCreateRequest(
        user={"client_user_id": str(request.user.id)},
        client_name="MoneyParce",
        products=[Products("transactions")],
        country_codes=[CountryCode("US")],
        language="en"
    )

    response = client.link_token_create(request_data)
    return JsonResponse(response.to_dict())

@csrf_exempt
@login_required
def exchange_public_token(request):
    body = json.loads(request.body)
    public_token = body.get('public_token')

    configuration = plaid.Configuration(
        host=plaid.Environment.Sandbox,
        api_key={
            'clientId': settings.PLAID_CLIENT_ID,
            'secret': settings.PLAID_SECRET
        }
    )
    client = get_plaid_client()

    exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
    exchange_response = client.item_public_token_exchange(exchange_request)

    PlaidItem.objects.update_or_create(
        user=request.user,
        defaults={
            'access_token': exchange_response.access_token,
            'item_id': exchange_response.item_id
        }
    )
    return JsonResponse({'status': 'access token saved'})

@login_required
def fetch_transactions(request):
    try:
        plaid_item = PlaidItem.objects.get(user=request.user)
    except PlaidItem.DoesNotExist:
        return JsonResponse({'error': 'No linked Plaid account'}, status=400)

    configuration = plaid.Configuration(
        host=plaid.Environment.Sandbox,
        api_key={
            'clientId': settings.PLAID_CLIENT_ID,
            'secret': settings.PLAID_SECRET
        }
    )
    client = get_plaid_client()

    end_date = datetime.datetime.today()
    start_date = end_date - datetime.timedelta(days=30)

    request_data = TransactionsGetRequest(
        access_token=plaid_item.access_token,
        start_date=start_date.date(),
        end_date=end_date.date(),
        options=TransactionsGetRequestOptions(count=20)
    )

    response = client.transactions_get(request_data)
    transactions = response['transactions']

    for txn in transactions:
        amount = Decimal(txn['amount'])
        name = txn['name']
        Expense.objects.create(
            user=request.user,
            amount=amount,
            category=None,  # optional: match to a Budget
        )

    return JsonResponse({'status': 'imported', 'count': len(transactions)})

@login_required
def settings_view(request):
    return render(request, 'settings/settings.html')

def logout_view(request):
    logout(request)
    #return render(request, 'home/index.html')
    return redirect('/')

def get_plaid_client():
    configuration = plaid.Configuration(
        host=plaid.Environment.Sandbox,
        api_key={
            'clientId': settings.PLAID_CLIENT_ID,
            'secret': settings.PLAID_SECRET
        }
    )
    return plaid_api.PlaidApi(plaid.ApiClient(configuration))
