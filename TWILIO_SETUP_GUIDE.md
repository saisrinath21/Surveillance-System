# Twilio Setup & Debugging Guide

## Step 1: Verify Environment Variables

Open PowerShell in the `backend/` folder and check your `.env` file:

```powershell
# View your .env file to confirm all Twilio variables are set
Get-Content .env
```

**Required variables in `.env`:**
```
ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
AUTH_TOKEN=your_auth_token_here
FROM_NUMBER=+1234567890
```

**To find these:**
1. Go to https://www.twilio.com/console
2. Copy **Account SID** and **Auth Token** from the main page
3. Go to **Phone Numbers** > **Manage** > select your number
4. Copy the **Phone Number** (should look like `+1234567890`)

---

## Step 2: Test Environment Variables Are Loaded

Run this Python command in the `backend/` folder:

```powershell
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('ACCOUNT_SID:', os.getenv('ACCOUNT_SID')); print('AUTH_TOKEN:', os.getenv('AUTH_TOKEN')); print('FROM_NUMBER:', os.getenv('FROM_NUMBER'))"
```

**Expected output:** Should show your actual credentials (not empty)

---

## Step 3: Test Twilio Connection

Create a test script `test_twilio.py` in the backend folder:

```python
from dotenv import load_dotenv
import os
from twilio.rest import Client

load_dotenv()

ACCOUNT_SID = os.getenv('ACCOUNT_SID')
AUTH_TOKEN = os.getenv('AUTH_TOKEN')
FROM_NUMBER = os.getenv('FROM_NUMBER')

print(f"Account SID: {ACCOUNT_SID}")
print(f"Auth Token: {AUTH_TOKEN[:10]}..." if AUTH_TOKEN else "Auth Token: NOT SET")
print(f"From Number: {FROM_NUMBER}")

if not all([ACCOUNT_SID, AUTH_TOKEN, FROM_NUMBER]):
    print("\n❌ ERROR: One or more credentials are missing!")
    exit(1)

try:
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    print("\n✓ Twilio client connected successfully!")
    
    # Try to fetch account details
    account = client.api.accounts(ACCOUNT_SID).fetch()
    print(f"✓ Account Status: {account.status}")
    print(f"✓ Account Balance: ${account.balance}")
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    print("Check your ACCOUNT_SID and AUTH_TOKEN are correct")
```

Run it:
```powershell
python test_twilio.py
```

**Expected output:** Should show "✓ Twilio client connected successfully!" and your account balance

---

## Step 4: Test Making a Call

**⚠️ WARNING: This will make a real call to the phone number!**

Create `test_call.py` in the backend folder:

```python
from dotenv import load_dotenv
import os
from twilio.rest import Client
import re

load_dotenv()

ACCOUNT_SID = os.getenv('ACCOUNT_SID')
AUTH_TOKEN = os.getenv('AUTH_TOKEN')
FROM_NUMBER = os.getenv('FROM_NUMBER')

def format_indian_phone_number(number):
    """Normalize Indian mobile numbers for Twilio calls"""
    digits = re.sub(r'\D', '', str(number))
    if digits.startswith('0'):
        digits = digits[1:]
    if digits.startswith('91') and len(digits) == 12:
        return f'+{digits}'
    if len(digits) == 10:
        return f'+91{digits}'
    raise ValueError("Invalid Indian mobile number. Provide a 10-digit Indian number.")

try:
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    
    # Replace with your own number to test
    TEST_PHONE_NUMBER = "9876543210"  # Change this!
    formatted_number = format_indian_phone_number(TEST_PHONE_NUMBER)
    
    print(f"From: {FROM_NUMBER}")
    print(f"To: {formatted_number}")
    print(f"TwiML: Say 'This is a test call'")
    print("\nInitiating call...")
    
    call = client.calls.create(
        from_=FROM_NUMBER,
        to=formatted_number,
        twiml='<Response><Say>This is a test call from your Surveillance System</Say></Response>'
    )
    
    print(f"✓ Call initiated! SID: {call.sid}")
    print(f"Check your phone or Twilio Console for the call")
    
except Exception as e:
    print(f"❌ ERROR: {str(e)}")
    print("\nCommon issues:")
    print("- Trial account: Phone numbers must be verified in Twilio Console")
    print("- Incorrect phone format: Use 10-digit Indian numbers (9876543210)")
    print("- Insufficient balance: Check your Twilio account balance")
```

Run it:
```powershell
python test_call.py
```

**Replace `9876543210` with YOUR phone number before running!**

---

## Step 5: Run Backend & Check Logs

```powershell
cd backend
python app.py
```

Watch the console output for errors. When you trigger an alert, you should see:

```
[✓] Call alert sent. Call SID: CA1234567890abcdef
```

---

## Step 6: Check Twilio Console for Failures

If calls aren't going through:

1. Go to https://www.twilio.com/console/phone-numbers/incoming
2. Click on your phone number
3. Scroll down to **Recent Calls**
4. Click on any failed calls to see the error message

**Common errors:**
- `Invalid phone format` → Number not in E.164 format
- `Permission to call number denied` → Number needs to be verified (trial account)
- `No credits` → Need to add payment method
- `Invalid request` → TwiML syntax error

---

## Step 7: Verify Phone Numbers for Trial Account

If you have a **Trial Account**, you must verify phone numbers:

1. Go to https://www.twilio.com/console/phone-numbers/verified
2. Click **Verify a number**
3. Enter the phone number you want to call
4. Twilio will send a code via SMS
5. Enter the code to verify

---

## Quick Checklist

- [ ] `.env` file exists in `backend/` folder
- [ ] `ACCOUNT_SID`, `AUTH_TOKEN`, `FROM_NUMBER` are set in `.env`
- [ ] Run `test_twilio.py` and see "✓ Twilio client connected successfully!"
- [ ] Account has balance (check in Twilio Console)
- [ ] For trial accounts: Phone numbers are verified
- [ ] Phone numbers are in correct format (10 digits for India)
- [ ] Backend runs without errors: `python app.py`

---

## If Still Not Working

Run this diagnostic:
```powershell
python test_twilio.py
```

Then copy the error message and:
1. Check Twilio documentation: https://www.twilio.com/docs/voice/make-calls
2. Check error code in Twilio Console
3. Verify your credentials haven't expired
