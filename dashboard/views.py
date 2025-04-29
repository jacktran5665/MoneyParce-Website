from django.contrib.auth.decorators import login_required
from django.shortcuts               import render, redirect
from decimal                        import Decimal
from django.http                    import JsonResponse
from django.views.decorators.csrf   import csrf_exempt
from django.contrib import messages               
from django.db.models import Sum
from django.contrib.auth            import logout
from django.contrib.humanize.templatetags.humanize import intcomma

from plaid.api                      import plaid_api
from plaid.model.link_token_create_request          import LinkTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.transactions_get_request           import TransactionsGetRequest
from plaid.model.transactions_get_request_options   import TransactionsGetRequestOptions
from plaid.model.country_code                       import CountryCode
from plaid.model.products                           import Products
import plaid
import datetime
import json

from django.conf   import settings
from .models       import Income, Expense, Budget, PlaidItem


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
                messages.error(request, "Please select a budget category before adding an expense.")
                return redirect('dashboard')

            try:
                budget_obj = Budget.objects.get(id=bid, user=request.user)
            except Budget.DoesNotExist:
                messages.error(request, "Selected budget category does not exist.")
                return redirect('dashboard')

            spent = (Expense.objects
                     .filter(category=budget_obj, user=request.user)
                     .aggregate(total=Sum('amount'))['total'] or Decimal('0'))

            over_budget = spent - budget_obj.total_budget
            future_spent = spent + amt - budget_obj.total_budget

            if over_budget > 0:
                messages.error(
                    request,
                    f'{budget_obj.name} is over budget by ${future_spent:.2f} Ease up on spending!'
                )
            elif future_spent > 0:
                messages.error(
                    request,
                    f'Adding ${amt:.2f} exceeds {budget_obj.name} by ${future_spent:.2f} Watch your spending!'
                )

            Expense.objects.create(
                user     = request.user,
                amount   = amt,
                category = budget_obj
            )
            return redirect('dashboard')

        elif 'submit_budget' in request.POST:
            name = request.POST.get('budget_name', '').strip()
            tot  = Decimal(request.POST.get('total_budget_new', '0') or '0')
            if name:
                Budget.objects.create(user=request.user, name=name, total_budget=tot)

        elif 'update_budget' in request.POST:
            bid  = request.POST.get('budget_id')
            name = request.POST.get('budget_name', '').strip()
            tot  = Decimal(request.POST.get('total_budget_new', '0') or '0')
            try:
                budget_obj = Budget.objects.get(id=bid, user=request.user)
                if name:
                    budget_obj.name = name
                budget_obj.total_budget = tot
                budget_obj.save()
            except Budget.DoesNotExist:
                messages.error(request, "Budget not found.")
            return redirect('dashboard')
        
        elif 'delete_budget' in request.POST:
            bid = request.POST.get('budget_id')
            try:
                Budget.objects.get(id=bid, user=request.user).delete()
            except Budget.DoesNotExist:
                messages.error(request, "Budget not found.")
            return redirect('dashboard')

        return redirect('dashboard')

    incomes   = Income.objects.filter(user=request.user)
    expenses  = Expense.objects.filter(user=request.user)
    budgets   = Budget.objects.filter(user=request.user).order_by('id')

    total_income_raw      = sum(i.amount for i in incomes)
    total_expenses_raw    = sum(e.amount for e in expenses)
    remaining_balance_raw = total_income_raw - total_expenses_raw

    total_income      = total_income_raw
    total_expenses    = total_expenses_raw
    remaining_balance = remaining_balance_raw

    ctx = {
        'total_income'       : intcomma(total_income),
        'total_expenses'     : intcomma(total_expenses),
        'remaining_balance'  : intcomma(remaining_balance),
        'expense_over_income': f"{(total_expenses_raw / total_income_raw * 100):.2f}%"
                               if total_income_raw else "0.00%",
        'budgets'            : budgets,
    }
    return render(request, 'dashboard/dashboard.html', ctx)

@login_required
def create_link_token(request):
    configuration = plaid.Configuration(
        host=plaid.Environment.Sandbox,
        api_key={'clientId': settings.PLAID_CLIENT_ID, 'secret': settings.PLAID_SECRET}
    )
    client = get_plaid_client()

    req = LinkTokenCreateRequest(
        user={"client_user_id": str(request.user.id)},
        client_name="MoneyParce",
        products=[Products("transactions")],
        country_codes=[CountryCode("US")],
        language="en"
    )
    return JsonResponse(client.link_token_create(req).to_dict())


@csrf_exempt
@login_required
def exchange_public_token(request):
    public_token = json.loads(request.body).get('public_token')
    client       = get_plaid_client()
    exchange     = client.item_public_token_exchange(
                      ItemPublicTokenExchangeRequest(public_token=public_token))

    PlaidItem.objects.update_or_create(
        user=request.user,
        defaults={'access_token': exchange.access_token, 'item_id': exchange.item_id}
    )
    return JsonResponse({'status': 'access token saved'})


@login_required
def fetch_transactions(request):
    try:
        plaid_item = PlaidItem.objects.get(user=request.user)
    except PlaidItem.DoesNotExist:
        return JsonResponse({'error': 'No linked Plaid account'}, status=400)

    client     = get_plaid_client()
    end_date   = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=30)

    req = TransactionsGetRequest(
        access_token=plaid_item.access_token,
        start_date=start_date,
        end_date=end_date,
        options=TransactionsGetRequestOptions(count=20)
    )
    txns = client.transactions_get(req)['transactions']

    for t in txns:
        amount   = Decimal(t['amount'])
        name     = t['name']
        categories = t.get('category', [])

        # skip transfers
        if categories and 'Transfer' in categories:
            continue

        # map Plaid category → Budget
        matched_budget = None
        for cat in categories:
            budget_name = PLAID_CATEGORY_TO_BUDGET.get(cat)
            if budget_name:
                matched_budget = Budget.objects.filter(
                                    user=request.user, name__iexact=budget_name
                                 ).first()
                if matched_budget:
                    break
        if not matched_budget:
            matched_budget, _ = Budget.objects.get_or_create(
                                    user=request.user,
                                    name="Uncategorized",
                                    defaults={'total_budget': 0})

        Expense.objects.create(
            user=request.user,
            amount=amount,
            merchant_name=name,
            category=matched_budget
        )

    return JsonResponse({'status': 'imported', 'count': len(txns)})


@login_required
def settings_view(request):
    return render(request, 'settings/settings.html')


def logout_view(request):
    logout(request)
    return redirect('/')


def get_plaid_client():
    configuration = plaid.Configuration(
        host=plaid.Environment.Sandbox,
        api_key={'clientId': settings.PLAID_CLIENT_ID, 'secret': settings.PLAID_SECRET}
    )
    return plaid_api.PlaidApi(plaid.ApiClient(configuration))


PLAID_CATEGORY_TO_BUDGET = {
    # Food related
    'Food and Drink': 'Food & Drink',
    'Coffee Shop': 'Food & Drink',
    'Restaurants': 'Food & Drink',
    'Fast Food': 'Food & Drink',
    'Bars': 'Food & Drink',
    # Groceries
    'Groceries': 'Groceries',
    'Supermarkets and Groceries': 'Groceries',
    'Convenience Stores': 'Groceries',
    # Transportation
    'Gas': 'Transportation',
    'Taxi': 'Transportation',
    'Ride Share': 'Transportation',
    'Parking': 'Transportation',
    'Public Transportation': 'Transportation',
    'Car Rental': 'Transportation',
    'Tolls and Fees': 'Transportation',
    # Entertainment
    'Movies': 'Entertainment',
    'Music and Video': 'Entertainment',
    'Concerts': 'Entertainment',
    'Video Games': 'Entertainment',
    'Amusement Parks': 'Entertainment',
    'Arts and Crafts': 'Entertainment',
    'Recreation': 'Entertainment',
    'Shops': 'Transportation',
    # Travel
    'Travel': 'Travel',
    'Hotel': 'Travel',
    'Airlines and Aviation Services': 'Travel',
    'Bus Lines': 'Travel',
    'Cruises': 'Travel',
    # Health & Fitness
    'Pharmacies': 'Health',
    'Doctor': 'Health',
    'Dentist': 'Health',
    'Eyecare': 'Health',
    # Bank fees and payments
    'Credit Card Payment': 'Fees & Payments',
    'Bank Fees': 'Fees & Payments',
    'Loan Payment': 'Fees & Payments',
    'Mortgage Payment': 'Fees & Payments',
    'Payment': 'Fees & Payments',
    # Savings
    'Investments': 'Savings',
    'Retirement': 'Savings',
    'Savings': 'Savings',
}
