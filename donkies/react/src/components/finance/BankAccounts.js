import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import autoBind from 'react-autobind'
import { Link } from 'react-router'
import { TableSimple } from 'components'


class BankAccounts extends Component{
    constructor(props){
        super(props)
        autoBind(this)
    }

    onClickRemove(accountId){
        console.log('remove account')
        console.log(accountId)
    }

    /**
     * Prepare data for table.
     */
    getData(accounts){
        let data = {}
        data.id = 'accounts'
        data.header = [
            'BANK', 'NAME', 'BALANCE', 'TRANSACTIONS']
        data.rows = []

        for (let a of accounts){
            let row = {}
            row.cols = []

            let col
            col = {
                value: <a target="_blank" href={a.institution.url}>{a.institution.name}</a>
            }
            row.cols.push(col)
            row.cols.push({value: a.name})
            row.cols.push({value: '$' + a.balance})

            const link = (<Link to={'/transactions?account_id=' + a.id}>
                            <i style={{fontSize: '25px'}} className="zmdi zmdi-view-list" />
                        </Link>)
            row.cols.push({value: link})
            data.rows.push(row)
        }
        return data
    }

    render(){
        const { accounts } = this.props
        if (!accounts || accounts.length === 0){
            return null
        }

        return (
            <TableSimple data={this.getData(accounts)} />
        )
    }
}


BankAccounts.propTypes = {
    accounts: PropTypes.array
}

const mapStateToProps = (state) => ({
    accounts: state.accounts.items
})

export default connect(mapStateToProps, {
})(BankAccounts)