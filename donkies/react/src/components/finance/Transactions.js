import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import autoBind from 'react-autobind'
import { LoadingInline, TableData } from 'components'


class Transactions extends Component{
    constructor(props){
        super(props)
        autoBind(this)
    }

    /**
     * Prepare data for table.
     */
    getData(transactions){
        let data = {}
        data.id = 'transactions'
        data.header = [
            'Date', 'Account', 'Amount', 'Roundup', 'Description']
        data.rows = []

        for (let t of transactions){
            let row = {}
            row.cols = []

            row.cols.push({value: t.created_at})
            row.cols.push({value: t.account})
            row.cols.push({value: `$${t.amount}`})
            row.cols.push({value: `$${t.roundup}`})
            row.cols.push({value: t.description})
            data.rows.push(row)
        }
        return data
    }

    render(){
        const { transactions } = this.props
        
        if (!transactions){
            return <LoadingInline />
        }

        const data = this.getData(transactions)

        return (
            <wrap>
                <h3>{'Transactions'}</h3>

                <div>
                    {'TODO: Show select with accounts. If account passed via GET param, autoselect it.'}
                </div>
                <br /><br />

                <TableData
                    data={data}
                    searchFields={['account', 'description']} />
            </wrap>
        )
    }
}


Transactions.propTypes = {
    transactions: PropTypes.array
}

const mapStateToProps = (state) => ({
    transactions: state.transactions.items
})

export default connect(mapStateToProps, {
})(Transactions)