from brownie import (network, config, interface)

from scripts.helpful_scripts import (
    get_account,
    get_weth,
    get_asset_price,
    get_lending_pool,
    get_borrowable_data,
    approve_erc20,
    )
from scripts.aave_borrow import (repay_all, amount, rate_mode)

from web3 import Web3



def test_get_borrowable_data_without_borrowing():
    # Arrange
    lending_pool = get_lending_pool()
    account = get_account()
    # Act
    borrowable_eth, total_debt = get_borrowable_data(lending_pool, account)
    # Assert
    assert borrowable_eth == 0
    assert type(borrowable_eth) == float
    assert total_debt == 0
    assert type(total_debt) == float


def test_get_borrowable_data_having_deposited():
    # Arrange
    lending_pool = get_lending_pool()
    account = get_account()
    
    get_weth(amount)
    spender = get_lending_pool()
    erc20_address = interface.IWeth(
        config['networks'][network.show_active()]['weth_token']
        ).address
    # Act
    erc20_approve_tx = approve_erc20(amount, spender.address, erc20_address, account)
    lending_pool.deposit(erc20_address, amount, account.address, 0, {"from": account})
    borrowable_eth, total_debt = get_borrowable_data(lending_pool, account)
    # Assert
    assert borrowable_eth > 0
    assert type(borrowable_eth) == float
    assert total_debt == 0
    assert type(total_debt) == float


def test_get_borrowable_data_having_borrowed():
    # Arrange
    lending_pool = get_lending_pool()
    account = get_account()
    
    get_weth(amount)
    spender = get_lending_pool()
    erc20_address = interface.IWeth(
        config['networks'][network.show_active()]['weth_token']
        ).address
    
    dai_address = config['networks'][network.show_active()]['dai_token']
    dai_eth_price = get_asset_price(
        config['networks'][network.show_active()]['dai_eth_price_feed']
    )
    # Act
    erc20_approve_tx = approve_erc20(amount, spender.address, erc20_address, account)
    tx = lending_pool.deposit(erc20_address, amount, account.address, 0, {"from": account})
    tx.wait(1)
    initial_borrowable_eth, initial_total_debt = get_borrowable_data(lending_pool, account)
    amount_dai_to_borrow = (1 / dai_eth_price) * initial_borrowable_eth * 0.5
    print(f"Asking to borrow {amount_dai_to_borrow} DAI or {Web3.toWei(amount_dai_to_borrow, 'ether')} in WEI units ...")
    lending_pool.borrow(
        dai_address,
        Web3.toWei(amount_dai_to_borrow, "ether"),
        rate_mode,
        0,
        account.address,
        {"from": account},
    )
    borrowable_eth, total_debt = get_borrowable_data(lending_pool, account)
    # Assert
    assert borrowable_eth < initial_borrowable_eth
    assert total_debt > initial_total_debt
    
    
def test_repay_all():
        # Arrange
    lending_pool = get_lending_pool()
    account = get_account()
    
    get_weth(amount)
    spender = get_lending_pool()
    erc20_address = interface.IWeth(
        config['networks'][network.show_active()]['weth_token']
        ).address
    
    dai_address = config['networks'][network.show_active()]['dai_token']
    dai_eth_price = get_asset_price(
        config['networks'][network.show_active()]['dai_eth_price_feed']
    )
    erc20_approve_tx = approve_erc20(amount, spender.address, erc20_address, account)
    tx = lending_pool.deposit(erc20_address, amount, account.address, 0, {"from": account})
    tx.wait(1)
    initial_borrowable_eth, initial_total_debt = get_borrowable_data(lending_pool, account)
    amount_dai_to_borrow = (1 / dai_eth_price) * initial_borrowable_eth * 0.5
    print(f"Asking to borrow {amount_dai_to_borrow} DAI or {Web3.toWei(amount_dai_to_borrow, 'ether')} in WEI units ...")
    lending_pool.borrow(
        dai_address,
        Web3.toWei(amount_dai_to_borrow, "ether"),
        rate_mode,
        0,
        account.address,
        {"from": account},
    )
    borrowable_eth, total_debt = get_borrowable_data(lending_pool, account)
    
    # Act
    repay_all(total_debt, lending_pool, account)
    
    # Assert
    assert total_debt == 0