from scripts.helpful_scripts import (
    get_account,
    get_weth,
    get_asset_price,
    get_borrowable_data,
    get_lending_pool,
    approve_erc20
    )
from brownie import interface, network, config, interface
from web3 import Web3

amount = Web3.toWei(0.05, 'ether')
rate_mode = 1   


def main():
    account = get_account()
    erc20_address = interface.IWeth(config['networks'][network.show_active()]['weth_token'])
    # if network.show_active() in ["mainnet-fork"]:
    get_weth(amount)
    lending_pool = get_lending_pool()
    # Aproving the following deposit
    approve_erc20(amount, lending_pool.address, erc20_address.address, account)
    tx = lending_pool.deposit(erc20_address, amount, account.address, 0, {"from": account})
    print("Depositing")
    tx.wait(1)  
    print("Deposited")
    borrowable_eth, total_debt = get_borrowable_data(lending_pool, account)
    print("Let's borrow some DAI")
    # We need DAI in terms of ETH
    dai_eth_price = get_asset_price(
        config["networks"][network.show_active()]["dai_eth_price_feed"]
    )
    health_value = 0.95 # This is for not exceeding the health factor when borrowing
    # This (1 / dai_eth_price) is for working with eth and eth units
    amount_dai_to_borrow = (1 / dai_eth_price) * (borrowable_eth * health_value)
    # borrowable_Eth -> borrowable_dai * 95%
    print(f"We are going to borrow {amount_dai_to_borrow} DAI")
    dai_address = config['networks'][network.show_active()]['aave_dai_token']

    borrow_tx = lending_pool.borrow(
        dai_address, 
        Web3.toWei(amount_dai_to_borrow, "ether"), # Always in WEI when is a tx
        rate_mode, # InterestRateMode: 1-> Stable, 2-> Variable
        0, # Refferal code
        account.address, # OnBehalfOf 
        {"from": account} # For paying gas of transaction
    )
    borrow_tx.wait(1)
    print(f"We borrowed some DAI")
    get_borrowable_data(lending_pool, account)
    repay_all(amount_dai_to_borrow, lending_pool, account)
    get_borrowable_data(lending_pool, account)
    

def repay_all(amount, lending_pool, account):
    # 1st: Approve the pay back
    approve_erc20(
        Web3.toWei(amount, "ether"),
        lending_pool.address, 
        config['networks'][network.show_active()]['aave_dai_token'],
        account,
        )   
    # 2nd: Pay back
    print("Repaying all...")
    repay_tx = lending_pool.repay(
        config['networks'][network.show_active()]['aave_dai_token'],
        Web3.toWei(amount, 'ether'), # Using -1 means repay all
        rate_mode,
        account.address,
        {"from": account},
    )
    repay_tx.wait(1)
    print(f"Repayed a total of {Web3.toWei(amount, 'ether')} DAI")
    

if __name__ == '__main__':
    main()