import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import autoBind from 'react-autobind'
import { Link } from 'react-router'
import { getDollarAmount } from 'services/helpers'
import {
    AccountRemove,
    CardSimple,
    Modal,
    ShareEdit,
    TableSimple } from 'components'


class DebtAccounts extends Component{
    constructor(props){
        super(props)
        autoBind(this)

        this.state = {
            isShowRemoveModal: false,
            isShowShareModal: false
        }
    }

    onClickShowShareModal(){
        this.setState({isShowShareModal: true})
    }

    onClickCloseShareModal(){
        this.setState({isShowShareModal: false})
    }

    onClickShowRemoveModal(){
        this.setState({isShowRemoveModal: true})
    }

    onClickCloseRemoveModal(){
        this.setState({isShowRemoveModal: false})
    }

    onAccountRemoved(){
        this.setState({isShowRemoveModal: false})   
    }

    hasAccounts(){
        const { accounts } = this.props

        if (accounts && accounts.length > 0){
            return true
        }
        return false
    }

    /**
     * Prepare data for table.
     */
    getData(accounts){
        let data = {}
        data.id = 'debtAccounts'
        data.header = [
            'LENDER', 'ACCOUNT NAME', 'BALANCE', 'TRANSFER SHARE', 'TRANSACTIONS']
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
            row.cols.push({value: `${a.transfer_share}%`})

            const link = (<Link to={'/transactions?account_id=' + a.id}>
                            <i style={{fontSize: '25px'}} className="zmdi zmdi-view-list" />
                        </Link>)
            row.cols.push({value: link})
            data.rows.push(row)
        }
        return data
    }

    render(){
        const { isShowRemoveModal, isShowShareModal } = this.state
        const { accounts } = this.props
        
        return (
            <wrap>
                {this.hasAccounts() &&
                    <Modal
                        onClickClose={this.onClickCloseRemoveModal}
                        visible={isShowRemoveModal}
                        title="Remove lender">
                            
                            <AccountRemove
                                onAccountRemoved={this.onAccountRemoved}
                                accounts={accounts} />
                    </Modal>  
                }

                {(this.hasAccounts() && accounts.length > 1) &&
                    <Modal
                        onClickClose={this.onClickCloseShareModal}
                        visible={isShowShareModal}
                        title="Edit share of transfers">
                            
                            <ShareEdit accounts={accounts} />
                    </Modal>  
                }
                        
                <CardSimple
                    header="Lenders"
                    headerClass="m-b-20"
                    isContentToBody={false}>
                                    
                    <Link to="/add_lender" className="btn bgm-lightblue btn-icon-text btn-sm waves-effect m-r-5 m-t-5">
                        <i className="zmdi zmdi-plus" />
                        {'Add lender'}
                    </Link>

                    {(this.hasAccounts() && accounts.length > 1) &&
                        <button
                            onClick={this.onClickShowShareModal}
                            className="btn bgm-lightblue btn-icon-text btn-sm waves-effect m-r-5 m-t-5">
                            <i className="zmdi zmdi-edit" />
                            {'Edit share'}
                        </button>
                    }

                    {this.hasAccounts() &&
                        <button
                            onClick={this.onClickShowRemoveModal}
                            className="btn bgm-red btn-icon-text btn-sm waves-effect m-r-5 m-t-5">
                            <i className="zmdi zmdi-delete" />
                            {'Remove lender'}
                        </button>
                    }
                </CardSimple>

                {this.hasAccounts() && <TableSimple data={this.getData(accounts)} />}
                
            </wrap>
        )
    }
}


DebtAccounts.propTypes = {
    accounts: PropTypes.array
}

const mapStateToProps = (state) => ({
    accounts: state.accounts.debtAccounts
})

export default connect(mapStateToProps, {
})(DebtAccounts)