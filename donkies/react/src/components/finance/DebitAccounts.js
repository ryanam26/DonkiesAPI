import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import autoBind from 'react-autobind'
import { Link } from 'react-router'
import classNames from 'classnames'
import { apiGetRequest, navigate } from 'actions'
import { apiCall3, ACCOUNTS_SET_FUNDING_SOURCE_URL } from 'services/api'
import { getDollarAmount } from 'services/helpers'
import {
    AccountRemove,
    CardSimple,
    LoadingInline,
    Modal,
    TableSimple } from 'components'


class DebitAccounts extends Component{
    constructor(props){
        super(props)
        autoBind(this)

        this.state = {
            isShowRemoveModal: false,
            setSourceInProgressId: null
        }
    }

    onClickShowModal(){
        this.setState({isShowRemoveModal: true})
    }

    onClickCloseModal(){
        this.setState({isShowRemoveModal: false})
    }

    onAccountRemoved(){
        this.setState({isShowRemoveModal: false})   
    }

    onClickSetSource(params){
        const { id } = params
        this.setSourceRequest(id)
    }

    onClickCreateDwolla(params){
        const { uid } = params
        this.props.navigate('/create_funding_source?account_uid=' + uid)
    }

    async setSourceRequest(id){
        this.setState({setSourceInProgressId: id})

        const url = `${ACCOUNTS_SET_FUNDING_SOURCE_URL}/${id}`  
        const data = {}
        let response = await apiCall3(url, data, true)
        if (response.status === 201){
            this.props.apiGetRequest('accounts')
            this.setState({setSourceInProgressId: null})
        }
    }

    hasAccounts(){
        const { accounts } = this.props

        if (accounts && accounts.length > 0){
            return true
        }
        return false
    }

    /**
     * Returns col object for table depends on account.
     */
    getCol(account){
        const { user } = this.props
        let dwollaCustomerId = null

        if (user.dwolla_customer){
            dwollaCustomerId = user.dwolla_customer.dwolla_id    
        }

        let cn, params, onClick, value, title
        if (!account.is_dwolla_created){
            cn = 'zmdi-plus fake-link'
            params = {uid: account.uid}
            onClick = this.onClickCreateDwolla
            title = 'Create funding source'
        } else if (account.is_funding_source_for_transfer){
            cn = 'zmdi-money'
            params = null
            onClick = null
            title = 'Active funding source'
        } else {
            cn = 'zmdi-assignment fake-link'
            params = {id: account.id}
            onClick = this.onClickSetSource
            title = 'Set account as funding source'
        }

        cn = classNames('zmdi', cn)
        value = <i title={title} style={{fontSize: '25px'}} className={cn} />
        
        if (!dwollaCustomerId){
            value = '-'
        }

        return {value, onClick, params}
    }

    /**
     * Prepare data for table.
     */
    getData(accounts){
        let data = {}
        data.id = 'debitAccounts'
        data.header = [
            'BANK', 'ACCOUNT NAME', 'BALANCE', 'TRANSACTIONS', 'SOURCE']
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
            row.cols.push({value: getDollarAmount(a.balance)})

            const link = (<Link to={'/transactions?account_id=' + a.id}>
                            <i style={{fontSize: '25px'}} className="zmdi zmdi-view-list" />
                        </Link>)
            row.cols.push({value: link})
            
            col = this.getCol(a)

            if (a.id === this.state.setSourceInProgressId){
                col.value = <LoadingInline radius={10} />
            }
            row.cols.push(col)
            data.rows.push(row)
        }
        return data
    }

    render(){
        const { isShowRemoveModal } = this.state
        const { accounts } = this.props
        
        return (
            <wrap>
                {this.hasAccounts() &&
                    <Modal
                        onClickClose={this.onClickCloseModal}
                        visible={isShowRemoveModal}
                        title="Remove bank account">
                            
                            <AccountRemove
                                onAccountRemoved={this.onAccountRemoved}
                                accounts={accounts} />
                    </Modal>  
                }
            
                <CardSimple
                    header="Bank Accounts"
                    headerClass="m-b-20"
                    isContentToBody={false}>
                                    
                    <Link to="/transactions" className="btn btn-default btn-sm waves-effect m-r-5 m-t-5">
                        {'View Transactions'}
                    </Link>
                    
                    <Link to="/add_bank" className="btn bgm-lightblue btn-icon-text btn-sm waves-effect m-r-5 m-t-5">
                        <i className="zmdi zmdi-plus" />
                        {'Add Bank Account'}
                    </Link>

                    {this.hasAccounts() &&
                        <button
                            onClick={this.onClickShowModal}
                            className="btn bgm-red btn-icon-text btn-sm waves-effect m-r-5 m-t-5">
                            <i className="zmdi zmdi-delete" />
                            {'Remove Bank Account'}
                        </button>
                    }
                </CardSimple>

                {this.hasAccounts() && <TableSimple data={this.getData(accounts)} />}
                
            </wrap>
        )
    }
}


DebitAccounts.propTypes = {
    accounts: PropTypes.array,
    apiGetRequest: PropTypes.func,
    navigate: PropTypes.func,
    user: PropTypes.object
}

const mapStateToProps = (state) => ({
    accounts: state.accounts.debitAccounts,
    user: state.user.item
})

export default connect(mapStateToProps, {
    apiGetRequest,
    navigate
})(DebitAccounts)