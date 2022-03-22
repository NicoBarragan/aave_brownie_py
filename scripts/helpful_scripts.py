from brownie import (
    network,
    accounts,
    config,
    interface,
)
from web3 import Web3

LOCAL_BLOCKCHAIN_ENVIRONMENTS = [
    "mainnet-fork",
    "binance-fork",
    "matic-fork",
]

def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return accounts[0]
    if id:
        return accounts.load(id)
    return accounts.add(config["wallets"]["from_key"])


def get_asset_price(price_feed):
    price_contract = interface.AggregatorV3Interface(price_feed)
    latest_price = price_contract.latestRoundData()[1]
    converted_latest_price = Web3.fromWei(latest_price, "ether") # From wei to eth
    print(f"The price of DAI/ETH is {converted_latest_price}")
    return float(converted_latest_price)


def get_weth(value):
    """
    Mints WETH by depositing ETH.
    """
    account = get_account()
    ## For interacting with WETH contract:
    # ABI --> The interface provides
    # Address --> We'll insert as the interface parameter
    weth = interface.IWeth(config['networks'][network.show_active()]['weth_token'])
    tx = weth.deposit({"from": account, "value": value})
    tx.wait(1)
    print("Received 0.1 WETH")
    # return tx
    

def approve_erc20(amount, spender, erc20_address, account):
    print("Aproving ERC20 token...")
    erc20 = interface.IERC20(erc20_address)
    tx = erc20.approve(spender, amount, {"from": account})
    tx.wait(1)
    print("Approved ERC20 token")
    return True


def get_lending_pool():
    # ABI
    # Address
    lending_pool_addresses_provider = interface.ILendingPoolAddressesProvider(
        config['networks'][network.show_active()]['lending_pool_addresses_provider']
        )
    lending_pool_address = lending_pool_addresses_provider.getLendingPool()
    # Now we use this address and the interface for get the lending pool
    lending_pool = interface.ILendingPool(lending_pool_address)
    return lending_pool


def get_borrowable_data(lending_pool, account):
    ( # The amounts are in WEI
        total_collateral_eth, # amount collateral we've
        total_debt_eth, # amount of debt we've
        available_borrow_eth, # amount of debt we can borrow
        current_liquidation_threshold, # threshlod = limite to get liquidated
        ltv, # % of the collateral that we can borrow
        health_factor,
        
        # is a view function so we don't spend gas
        # Nor need an account for paying the transaction        
    ) = lending_pool.getUserAccountData(account.address) 
## Converting to eth from wei:
    total_collateral_eth = Web3.fromWei(total_collateral_eth, 'ether')
    total_debt_eth = Web3.fromWei(total_debt_eth, 'ether')    
    available_borrow_eth = Web3.fromWei(available_borrow_eth, 'ether')
    print(f"You have {total_collateral_eth} worth of ETH deposited")
    print(f"You have {total_debt_eth} worth of ETH borrowed")
    print(f"You still can borrow {available_borrow_eth} worth of ETH")
    return (float(available_borrow_eth), float(total_debt_eth))