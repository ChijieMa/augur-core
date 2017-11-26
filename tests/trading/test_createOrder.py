#!/usr/bin/env python

from ethereum.tools import tester
from datetime import timedelta
from ethereum.tools.tester import TransactionFailed
from pytest import raises, fixture
from utils import bytesToLong, longTo32Bytes, longToHexString, bytesToHexString, fix, unfix, captureFilteredLogs, EtherDelta, stringToBytes
from uuid import uuid4
from constants import BID, ASK, YES, NO

tester.STARTGAS = long(6.7 * 10**6)

ATTOSHARES = 0
DISPLAY_PRICE = 1
OWNER = 2
TOKENS_ESCROWED = 3
SHARES_ESCROWED = 4
BETTER_ORDER_ID = 5
WORSE_ORDER_ID = 6
GAS_PRICE = 7

def test_publicCreateOrder_bid(contractsFixture, cash, market):
    orders = contractsFixture.contracts['Orders']
    createOrder = contractsFixture.contracts['CreateOrder']

    orderID = createOrder.publicCreateOrder(BID, 1, 10**17, market.address, 1, longTo32Bytes(0), longTo32Bytes(0), "7", value = 10**17)
    assert orderID

    assert orders.getAmount(orderID) == 1
    assert orders.getPrice(orderID) == 10**17
    assert orders.getOrderCreator(orderID) == bytesToHexString(tester.a0)
    assert orders.getOrderMoneyEscrowed(orderID) == 10**17
    assert orders.getOrderSharesEscrowed(orderID) == 0
    assert orders.getBetterOrderId(orderID) == bytearray(32)
    assert orders.getWorseOrderId(orderID) == bytearray(32)

def test_publicCreateOrder_ask(contractsFixture, cash, market):
    orders = contractsFixture.contracts['Orders']
    createOrder = contractsFixture.contracts['CreateOrder']

    orderID = createOrder.publicCreateOrder(ASK, 1, 10**17, market.address, 0, longTo32Bytes(0), longTo32Bytes(0), "7", value = 10**18)

    assert orders.getAmount(orderID) == 1
    assert orders.getPrice(orderID) == 10**17
    assert orders.getOrderCreator(orderID) == bytesToHexString(tester.a0)
    assert orders.getOrderMoneyEscrowed(orderID) == 10**18 - 10**17
    assert orders.getOrderSharesEscrowed(orderID) == 0
    assert orders.getBetterOrderId(orderID) == bytearray(32)
    assert orders.getWorseOrderId(orderID) == bytearray(32)
    assert cash.balanceOf(market.address) == 10**18 - 10**17

def test_publicCreateOrder_bid2(contractsFixture, cash, market, universe):
    orders = contractsFixture.contracts['Orders']
    createOrder = contractsFixture.contracts['CreateOrder']
    logs = []

    orderType = BID
    amount = 1
    fxpPrice = fix('0.6')
    outcome = 0
    tradeGroupID = "42"

    marketInitialCash = cash.balanceOf(market.address)
    captureFilteredLogs(contractsFixture.chain.head_state, contractsFixture.contracts['Augur'], logs)
    creatorInitialETH = contractsFixture.chain.head_state.get_balance(tester.a1)
    orderID = createOrder.publicCreateOrder(orderType, amount, fxpPrice, market.address, outcome, longTo32Bytes(0), longTo32Bytes(0), tradeGroupID, sender=tester.k1, value = fix('10'))
    assert orderID != bytearray(32), "Order ID should be non-zero"

    assert orders.getAmount(orderID) == amount
    assert orders.getPrice(orderID) == fxpPrice
    assert orders.getOrderCreator(orderID) == bytesToHexString(tester.a1)
    assert orders.getOrderMoneyEscrowed(orderID) == 0.6 * 10**18
    assert orders.getOrderSharesEscrowed(orderID) == 0
    assert cash.balanceOf(tester.a1) == 0
    assert contractsFixture.chain.head_state.get_balance(tester.a1) == creatorInitialETH - long(0.6 * 10**18)
    assert cash.balanceOf(market.address) - marketInitialCash == 0.6 * 10**18
    shareToken = contractsFixture.getShareToken(market, 0)
    assert len(logs) == 1
    assert logs[0]['_event_type'] == 'OrderCreated'
    assert logs[0]['creator'] == bytesToHexString(tester.a1)
    assert logs[0]['shareToken'] == shareToken.address
    assert logs[0]['tradeGroupId'] == stringToBytes("42")
    assert logs[0]['orderId'] == orderID

def test_createOrder_failure(contractsFixture, universe, cash, market):
    orders = contractsFixture.contracts['Orders']
    createOrder = contractsFixture.contracts['CreateOrder']
    fillOrder = contractsFixture.contracts['FillOrder']
    completeSets = contractsFixture.contracts['CompleteSets']
    yesShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(YES))
    noShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(NO))

    with raises(TransactionFailed):
        createOrder.createOrder(tester.a1, ASK, 1, fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), "42", sender=tester.k1)

    # createOrder exceptions (pre-escrowFunds)
    with raises(TransactionFailed):
        createOrder.publicCreateOrder(3, 1, fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), "42", sender=tester.k1)

    # escrowFundsForBid exceptions
    with raises(TransactionFailed):
        createOrder.publicCreateOrder(BID, 1, fix('3'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), "42", sender=tester.k1)
    with raises(TransactionFailed):
        createOrder.publicCreateOrder(BID, 1, fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), "42", sender=tester.k1)

    # escrowFundsForAsk exceptions
    with raises(TransactionFailed):
        createOrder.publicCreateOrder(ASK, 1, 1, market.address, YES, longTo32Bytes(0), longTo32Bytes(0), "42", sender=tester.k1)
    with raises(TransactionFailed):
        createOrder.publicCreateOrder(ASK, 1, fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), "42", sender=tester.k1)
    assert completeSets.publicBuyCompleteSets(market.address, 2, sender=tester.k1, value=fix('2'))
    with raises(TransactionFailed):
        createOrder.publicCreateOrder(ASK, 1, fix('3'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), "42", sender=tester.k1)

    assert yesShareToken.approve(createOrder.address, 12, sender=tester.k1) == 1, "Approve createOrder contract to spend shares from the user's account (account 1)"
    assert yesShareToken.allowance(tester.a1, createOrder.address) == 12, "CreateOrder contract's allowance should be equal to the amount approved"

    with raises(TransactionFailed):
        createOrder.publicCreateOrder(ASK, 1, fix('0.6'), tester.a1, YES, longTo32Bytes(0), longTo32Bytes(0), "42", sender=tester.k1)

    assert createOrder.publicCreateOrder(ASK, 1, fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), "42", sender=tester.k1) != 0, "Order ID should be non-zero"

    # createOrder exceptions (post-escrowFunds)
    with raises(TransactionFailed):
        createOrder.publicCreateOrder(ASK, 1, fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), "42", sender=tester.k1)

def test_ask_withPartialShares(contractsFixture, universe, cash, market):
    orders = contractsFixture.contracts['Orders']
    createOrder = contractsFixture.contracts['CreateOrder']
    fillOrder = contractsFixture.contracts['FillOrder']
    completeSets = contractsFixture.contracts['CompleteSets']
    yesShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(YES))
    noShareToken = contractsFixture.applySignature('ShareToken', market.getShareToken(NO))
    logs = []

    # buy 2 complete sets
    assert completeSets.publicBuyCompleteSets(market.address, 2, sender = tester.k1, value=fix('2'))
    assert cash.balanceOf(tester.a1) == fix('0')
    assert yesShareToken.balanceOf(tester.a1) == 2
    assert noShareToken.balanceOf(tester.a1) == 2

    logs = []
    captureFilteredLogs(contractsFixture.chain.head_state, contractsFixture.contracts['Augur'], logs)

    # create ASK order for 3 shares with a mix of shares and cash
    assert yesShareToken.approve(createOrder.address, fix('2'), sender = tester.k1)
    orderID = createOrder.publicCreateOrder(ASK, 3, fix('0.6'), market.address, YES, longTo32Bytes(0), longTo32Bytes(0), "42", sender=tester.k1, value=fix('0.4'))
    assert cash.balanceOf(tester.a1) == fix('0')
    assert yesShareToken.balanceOf(tester.a1) == 0
    assert noShareToken.balanceOf(tester.a1) == 2

    # Confirm create order logging works correctly
    assert len(logs) == 2
    assert logs[1]['_event_type'] == 'OrderCreated'
    assert logs[1]['creator'] == bytesToHexString(tester.a1)
    assert logs[1]['shareToken'] == yesShareToken.address
    assert logs[1]['tradeGroupId'] == stringToBytes("42")
    assert logs[1]['orderId'] == orderID

    # validate the order contains expected results
    assert orderID != bytearray(32), "Order ID should be non-zero"
    assert orders.getAmount(orderID) == 3
    assert orders.getPrice(orderID) == fix('0.6')
    assert orders.getOrderCreator(orderID) == bytesToHexString(tester.a1)
    assert orders.getOrderMoneyEscrowed(orderID) == fix('0.4')
    assert orders.getOrderSharesEscrowed(orderID) == 2

def test_duplicate_creation_transaction(contractsFixture, cash, market):
    orders = contractsFixture.contracts['Orders']
    createOrder = contractsFixture.contracts['CreateOrder']

    with EtherDelta(-10**17, tester.a0, contractsFixture.chain):
        orderID = createOrder.publicCreateOrder(BID, 1, 10**17, market.address, 1, longTo32Bytes(0), longTo32Bytes(0), "7", value = 10**17)

    assert orderID

    with raises(TransactionFailed):
        createOrder.publicCreateOrder(BID, 1, 10**17, market.address, 1, longTo32Bytes(0), longTo32Bytes(0), "7", value = 10**17)

def test_minimum_order(contractsFixture, cash, market):
    orders = contractsFixture.contracts['Orders']
    createOrder = contractsFixture.contracts['CreateOrder']

    with raises(TransactionFailed):
        createOrder.publicCreateOrder(BID, 1, 1, market.address, 1, longTo32Bytes(0), longTo32Bytes(0), "7", value = 1)

    with raises(TransactionFailed):
        createOrder.publicCreateOrder(ASK, 1, market.getNumTicks()-1, market.address, 1, longTo32Bytes(0), longTo32Bytes(0), "7", value = 1)

def test_publicCreateOrder_bid_real_example_case(contractsFixture, universe, cash):
    market = contractsFixture.createBinaryMarket(
            universe = universe,
            endTime = long(contractsFixture.chain.head_state.timestamp + timedelta(days=1).total_seconds()),
            feePerEthInWei = 10**16,
            denominationToken = cash,
            designatedReporterAddress = tester.a0,
            numTicks = 10752,
            sender = tester.k0,
            topic= "",
            extraInfo= "")

    orders = contractsFixture.contracts['Orders']
    createOrder = contractsFixture.contracts['CreateOrder']

    orderID = createOrder.publicCreateOrder(BID, 10000000000000, 2000, market.address, 0, longTo32Bytes(0), longTo32Bytes(0), 7, value = 20000000000000000)
    assert orderID

    assert orders.getAmount(orderID) == 10000000000000
    assert orders.getPrice(orderID) == 2000
    assert orders.getOrderCreator(orderID) == bytesToHexString(tester.a0)
    assert orders.getOrderMoneyEscrowed(orderID) == 20000000000000000
    assert orders.getOrderSharesEscrowed(orderID) == 0
    assert orders.getBetterOrderId(orderID) == bytearray(32)
    assert orders.getWorseOrderId(orderID) == bytearray(32)

def test_publicCreateOrder_bid_shares_escrowed(contractsFixture, universe, market, cash):
    completeSets = contractsFixture.contracts['CompleteSets']
    orders = contractsFixture.contracts['Orders']
    createOrder = contractsFixture.contracts['CreateOrder']

    # We'll buy 10 Complete Sets initially
    cost = 10 * market.getNumTicks()
    assert completeSets.publicBuyCompleteSets(market.address, 10, value=cost)

    # Now when we make a BID order for outcome 0 shares we will escrow outcome 1 shares instead of tokens when creating an order
    orderID = createOrder.publicCreateOrder(BID, 10, 5*10**17, market.address, 0, longTo32Bytes(0), longTo32Bytes(0), 7)
    assert orderID

    assert orders.getAmount(orderID) == 10
    assert orders.getPrice(orderID) == 5*10**17
    assert orders.getOrderCreator(orderID) == bytesToHexString(tester.a0)
    assert orders.getOrderMoneyEscrowed(orderID) == 0
    assert orders.getOrderSharesEscrowed(orderID) == 10
    assert orders.getBetterOrderId(orderID) == bytearray(32)
    assert orders.getWorseOrderId(orderID) == bytearray(32)
