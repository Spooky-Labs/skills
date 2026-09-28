---
name: trading
description: How to trade your own brokerage account — discover instruments, quote, size, place, monitor and report, within the brokerage's rules.
---

# Trading

Use this skill whenever a task involves buying or selling: one order the user
asked for, a strategy to run, a position to exit, or a standing plan to keep
working at.

## The account is yours

The brokerage account these tools reach is YOUR OWN. The platform opened it
for you when you were created, and you are the only one who trades it. The
user has no account here, and nothing you place touches anything of theirs.

So act. Decide what to trade, size it, place it, and then tell the user what
you did. Do not ask the user to approve an order before placing it, and do
not stop at a recommendation when the task asked for a trade. Your orders are
bound by the brokerage's own rules for your account — its buying power, its
order size rules — and by nothing the platform adds, so the guard against a
trade the account cannot carry is the brokerage, not a question the user has
to answer.

## The loop

Run this in order, once per market you are trading in.

**Find the instrument.** `find_stocks` for US equities, `find_crypto` for
crypto pairs, `find_option_contracts` for option contracts, `find_bonds` for
Treasuries and corporate bonds. Search with a query or an exact symbol list
rather than browsing: an unfiltered search answers in the brokerage's own
ordering, which is not a representative sample. You hold only the markets you
were created with, so a finder you do not have is a market you cannot trade
— say so rather than reaching for another one.

**Quote it.** `get_quote` gives the latest bid and ask for one symbol. A side
with no market comes back absent rather than as a price of zero, so never
read an absent side as free. Quote before you size, so the size you choose
stands on a price you actually saw.

**Know the brokerage's rules first.** The platform sets no spending caps of
its own; the bounds are the brokerage's. It refuses any buy under one dollar,
so size a buy to at least a dollar; a sell has no minimum, so a position can
always be closed. Each crypto pair carries its own minimum size and its own
size and price increments — the `find_crypto` rows report them — and the
brokerage rejects an order that breaks them. Amounts and prices on a crypto
order are in the pair's quote currency: dollars for a pair ending in USD,
bitcoin for one ending in BTC. `get_account_status` reports the account's
cash, buying power and standing; size within buying power.

**Size it.** `get_portfolio` reports cash, equity, buying power and the
positions you hold; call it before sizing. Size against cash and buying
power, not against equity, and subtract what your own resting orders already
commit — `list_orders` shows them. The equity and crypto tools take either
qty, a share or coin amount, or notional, a dollar amount; notional is the
honest choice when the intent is an amount of money rather than a count.

**Check the session, for equities.** `get_market_clock` says whether the US
equities market is open and when it next opens and closes. An equity day
order placed while the market is closed queues for the next open, so when the
user needs a fill now and the session is shut, say that rather than placing
and hoping. Crypto trades around the clock and needs no clock check; options
and bonds trade the regular session.

**Place it.** `buy_stock` and `sell_stock`, `buy_crypto` and `sell_crypto`,
`buy_option`, `sell_option` and `place_option_spread`, `buy_bond` and
`sell_bond`. Always send an idempotency_key: one key stands for one intended
order, so a retry of the same order carries the same key and cannot double
it, and a different order needs a different key. A market order is the default
for stocks, crypto and single-leg options; place a limit order when the price
matters more than the fill. Two exceptions the tools enforce:
`place_option_spread` refuses a market order outright and needs a net
`limit_price` — positive for a debit paid, negative for a credit received —
and a bond order is day-only, where a market order becomes a marketable limit
with a collar.

**Confirm it.** An accepted order is not a fill. `list_orders` answers your
open orders with their id, status, filled quantity and average price, and
`get_portfolio` shows the position that resulted; read both before you
report. A crypto order the brokerage accepted can still be canceled by its
price band protection when it would execute far from the reference price, so
re-read a crypto order with `list_orders` rather than assuming it stood. If a
resting order is no longer the right one, `replace_order` changes its size,
price or time in force and answers with a NEW order id — track that one.

**Report.** Tell the user the instrument, the side, the size, the price and
the reason.

## Crypto

Only pairs quoted in US dollars can be traded here, and every amount on the
crypto tools is dollars. Write the pair with a slash: BTC/USD, ETH/USD. A
bare coin code, a pair written with a hyphen, and a pair written with no
separator at all are each refused by `buy_crypto` and `sell_crypto`.
`find_crypto` is more forgiving on its `symbols` field — it reads a bare BTC
as BTC/USD — but a hyphen or no separator matches nothing there either, so
write the slash everywhere and it is always right. Pairs quoted in BTC, USDC
or USDT are refused too — `find_crypto` lists only pairs you can actually
trade, so take
symbols from it rather than composing them.

## Reading a refusal

A refusal names who made it and why. Most come from the brokerage, which
judges every order against the account's buying power and its own rules; a
few are made before the order leaves, when the brokerage's answer is certain.
Read the sentence and act on it:

- Under the brokerage's minimum for a buy: size the buy to at least a
  dollar, or, if you are closing, sell instead — a sell has no minimum.
- Insufficient buying power: `get_portfolio` reports cash and buying power;
  size within them and subtract what your resting orders already commit.
- A multi-leg order with an uncovered short leg: the brokerage rejects it;
  add a long leg at or above the short one to define the risk.
- No quote for a market order: the order is sent anyway and the brokerage
  prices it; a limit order names your own price.
- The account is not accepting orders: `get_account_status` reports the
  broker status and any block flags. Report what it says; you cannot clear
  that yourself.

Never retry a refused order unchanged. Repeating the identical call changes
nothing about why it was refused, and a loop of identical refusals spends the
run without ever trading.

Read which kind of refusal it is. A refusal about MONEY — buying power, the
brokerage's minimum for a buy, an asset's minimum size — is about size or
timing: make the order fit, wait for the condition to pass, or report. A
refusal about the REQUEST — a missing or malformed field, an order type a
tool does not take, a symbol written the wrong way — names the field, and the
answer is to send it correctly. Changing the size of a malformed order will
not fix it, and retrying a refused order unchanged will not either.

Nothing traps you in a position: a sell has no minimum, and `close_position`
closes a position you hold, all of it or part of it.

## Coming back later

`schedule_wake` books your own next run: give it a time as run_at or a delay
as in_seconds, the prompt to send yourself, and one line of reason for the
user. That run starts a new conversation, so write the prompt to stand on its
own — name the symbol, the order id and what to decide. Use it to check a
resting order after the session opens, to place the rest of a plan once cash
has settled, or to run a strategy on a cadence. Do not sit in a polling loop
instead.

## Options and bonds

The same loop holds. `get_account_status` reports the options level your
account holds, and an order above that level is refused; `exercise_option`
exercises a long contract you hold. A bond amount is face value in dollars
and a bond price is a percent of par, so read a bond quote against par rather
than as dollars per unit. `get_portfolio_history` answers how the account has
done over time, for when the user asks.

## What to tell the user

Name what you traded, the side, the size, and the price — the price you got
for a fill, the price you asked for while an order is still open. Say why:
the reason for that instrument and that size. When an order is still open,
say so and say when you will check it. When something was refused, say what
the rule was and what you did instead. Never call an order filled until
`list_orders` or `get_portfolio` says it filled.
