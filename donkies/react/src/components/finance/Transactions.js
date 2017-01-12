import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import autoBind from 'react-autobind'
import { LoadingInline, SelectSimple, TableData } from 'components'


/**
 * All transactions come from Redux state to props.
 * But component can filter transactions by some params.
 * getTransactions returns actual transactions after filtering.
 *
 * If query params contain "account_id", autoselect account in Select.
 */
class Transactions extends Component{
    constructor(props){
        super(props)
        autoBind(this)

        this.state = {
            accountId: null
        }
    }

    componentWillMount(){
        const { location } = this.props
        if (location.query.hasOwnProperty('account_id')){
            let id = parseInt(location.query.account_id)
            this.setState({accountId: id})
        }   
    }

    onChangeAccount(value){
        if (value === ''){
            value = null
        } else {
            value = parseInt(value)
        }
        this.setState({accountId: value})
    }

    /**
     * Returns options for SelectSimple for accounts.
     */
    getAccountsOptions(){
        const { accounts } = this.props
        let arr = []
        arr.push({value: '', text: '--- Select account'})

        for (let a of accounts){
            arr.push({value: a.id, text: a.name})
        }
        return arr
    }

    /**
     * Returns transactions after filtering.
     */ 
    getTransactions(){
        let { accounts, transactions } = this.props
        const { accountId } = this.state

        if (accountId){
            transactions = transactions.filter((t) => t.account_id === accountId)
        }
        return transactions
    }

  
    /**
     * Prepare data for table.
     */
    getData(){
        let data = {}
        data.id = 'transactions'
        data.header = [
            'Date', 'Account', 'Amount', 'Roundup', 'Description']
        data.rows = []

        for (let t of this.getTransactions()){
            let row = {}
            row.cols = []

            const roundup = t.roundup ? `$${t.roundup}` : '-'

            row.cols.push({value: t.created_at})
            row.cols.push({value: t.account})
            row.cols.push({value: `$${t.amount}`})
            row.cols.push({value: roundup})
            row.cols.push({value: t.description})
            data.rows.push(row)
        }
        return data
    }

    render(){
        const { transactions } = this.props
        let { accountId } = this.state

        if (!transactions){
            return <LoadingInline />
        }

        const data = this.getData()
        
        // Auto select account if it is passed in query params
        accountId = accountId || ''

        return (
            <wrap>
                <h3>{'Transactions'}</h3>

                <div className="row">
                    <div className="col-sm-4 col-xs-6">
                        <div className="card p-20">
                            <SelectSimple
                                name="accounts"
                                options={this.getAccountsOptions()}
                                onChange={this.onChangeAccount}
                                value={accountId} />
                        </div>
                    </div>
                </div>

                <TableData
                    data={data}
                    searchFields={['account', 'description']} />
            </wrap>
        )
    }
}


Transactions.propTypes = {
    accounts: PropTypes.array,
    location: PropTypes.object,
    transactions: PropTypes.array
}

const mapStateToProps = (state) => ({
    accounts: state.accounts.allAccounts,
    transactions: state.transactions.items
})

export default connect(mapStateToProps, {
})(Transactions)