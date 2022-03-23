from brownie import (network, config, interface)

from scripts.helpful_scripts import (
    get_account,
    get_weth,
    get_asset_price,
    get_lending_pool,
    approve_erc20,
    )
from scripts.aave_borrow import (repay_all, amount)

# Arrange
# Act
# Assert

def test_get_weth():
    # Arange
    account = get_account()
    initial_eth_balance = account.balance()
    # Act
    get_weth(amount)
    # assert
    assert account.balance() == initial_eth_balance - amount
    

def test_get_asset_price():
    asset_price = get_asset_price(
        config['networks'][network.show_active()]['dai_eth_price_feed']
        ) 
    assert asset_price > 0
    assert type(asset_price) == float


def test_get_lending_pool():
    assert get_lending_pool() != None
    

def test_get_approve_erc20():
    account = get_account()
    get_weth(amount)
    spender = get_lending_pool()
    erc20_address = interface.IWeth(
        config['networks'][network.show_active()]['weth_token']
        ).address
    erc20_approve_tx = approve_erc20(amount, spender.address, erc20_address, account)
    assert erc20_approve_tx == True