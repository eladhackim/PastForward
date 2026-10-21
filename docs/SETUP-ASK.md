# Setup: Ask PastForward (paid AI research)

**For Grok.** About 45 minutes of work, plus Lemon Squeezy's account review, which can take a day or two. Do sections 1 and 2 in parallel.

## What it is

Ask PastForward lets a subscriber type a question ("Is the AI boom like the dot-com bubble?"). An AI model answers in PastForward's Then → Today → Next format. Only paying users can ask. The code is already in the repo (`functions/api/ask/`). It stays switched off until `ASK_ENABLED=1`.

These protections are already built into the code. You don't set them up, but please know they exist:
- **Global spending cap:** $5 a month and $0.50 a day. The worst-case cost is reserved before every AI call, so the cap can't be crossed even under a burst of requests. A small model (Claude Haiku 5.5) costs about $0.0004 per question.
- **Per-subscriber allowance:** 30 questions a month.
- **Answer cache:** a repeated question is free and doesn't use up the allowance.
- **Licence check:** the key must come from our own Lemon Squeezy store and product.
- **No setup needed for the database tables:** they create themselves on first use.

## 1. Claude API key with its own spending limit (backstop)

In the Claude Console (platform.claude.com):

1. Create a workspace named **PastForward**.
2. In that workspace, open **Spend limits** and set the monthly limit to **$6**. This is a second, independent cap above the app's own $5.
3. Create an **API key inside the PastForward workspace**. Name it `pastforward-cloudflare`.
4. Make sure the organization has credit. A $10 prepayment is plenty.

Never put the key in the repo, in chat or in a file. It goes only into Cloudflare as a secret (section 3).

## 2. Lemon Squeezy (payments, taxes, licence keys)

Lemon Squeezy is the merchant of record, so it collects and files VAT and sales tax. We never touch card data.

1. Create an account and a store named **PastForward**. Set the store currency to **EUR**. Complete the identity and payout setup, which is required before live sales.
2. Create a product named **Ask PastForward**, as a **subscription**, with two variants:
   - **Monthly**: €3, billed every month
   - **Yearly**: €19, billed every year
3. On the product, switch on **Generate license keys** for both variants. Set the activation limit to unlimited (or 5) and the licence length to "unlimited". The subscription itself decides validity: when it ends, the key stops working.
4. Checkout and confirmation settings:
   - **Redirect URL after purchase:** `https://pastforward.app/#ask`
   - **Thank-you / receipt note:** "Copy your licence key, open PastForward, tap Ask and paste it once."
5. Write down:
   - **Store ID** (a number, from Settings → Stores)
   - **Product ID** (a number)
   - The **checkout link** for each variant (the product's Share button; it looks like `https://pastforward.lemonsqueezy.com/buy/…`)
   - The **customer portal** link (usually `https://pastforward.lemonsqueezy.com/billing`)
6. Do one purchase in **test mode** (card 4242 4242 4242 4242, any future date, any CVC) to get a test licence key for check 4.

## 3. Cloudflare Pages settings

Go to Workers & Pages → **pastforward** → Settings → **Variables and Secrets**, under **Production**.

| Name | Type | Value |
|---|---|---|
| `ANTHROPIC_API_KEY` | Secret | the key from section 1 |
| `ASK_OWNER_KEY` | Secret | a long random string, e.g. the output of `openssl rand -hex 24`. This is Elad's own free key for testing and demos. Send it to Elad privately. |
| `LS_STORE_ID` | Text | Store ID |
| `LS_PRODUCT_ID` | Text | Product ID |
| `LS_CHECKOUT_MONTHLY` | Text | monthly checkout link |
| `LS_CHECKOUT_YEARLY` | Text | yearly checkout link |
| `LS_PORTAL` | Text | customer portal link |
| `ASK_ENABLED` | Text | `1` (add this last, after the checks below pass with a preview deployment, or just before the final redeploy) |

**Optional.** These are the defaults; leave them out unless Elad asks for a change:
- `ASK_CAP_MONTH_USD=5`
- `ASK_CAP_DAY_USD=0.5`
- `ASK_MONTHLY=30`
- `ASK_MODEL=claude-haiku-5-5`
- `LS_PRICE_MONTHLY=€3`
- `LS_PRICE_YEARLY=€19`

The two price settings are display text only; real prices live in Lemon Squeezy.

Cloudflare applies variable changes only to new deployments. After saving, go to **Deployments → latest production deployment → Retry deployment**.

## 4. Checks (please send back the output)

```bash
# a. config: enabled true, the three links present
curl -s https://pastforward.app/api/ask/config

# b. owner key: ok true, left 30
curl -s -X POST https://pastforward.app/api/ask/status -H 'Content-Type: application/json' \
  -d '{"key":"<ASK_OWNER_KEY>"}'

# c. one real question with the owner key: an "answer" with then / now / next
curl -s -X POST https://pastforward.app/api/ask -H 'Content-Type: application/json' \
  -d '{"key":"<ASK_OWNER_KEY>","q":"Is the AI boom like the dot-com bubble?"}'

# d. the cost of that question was recorded (D1 console). Expect micro around 300-800, i.e. well under $0.001
SELECT * FROM ask_spend;

# e. the test-mode licence key from Lemon Squeezy: ok true
curl -s -X POST https://pastforward.app/api/ask/status -H 'Content-Type: application/json' \
  -d '{"key":"<TEST LICENCE KEY>"}'
```

## Running it

- **How much has it cost this month?** Run this in the D1 console:
  `SELECT substr(day,1,7) AS month, SUM(micro)/1e6 AS usd, SUM(calls) AS questions FROM ask_spend GROUP BY 1;`
- **Instant stop:** disable the API key in the Claude Console. Ask then shows "couldn't answer" and nothing is charged.
- **Clean stop:** set `ASK_ENABLED=0` and retry the deployment. Ask then shows "paused".
- **Growing:** if the $5 cap starts turning paying users away (roughly 300+ active subscribers), raise `ASK_CAP_MONTH_USD` and the Console workspace limit together. Only do this with Elad's approval.
