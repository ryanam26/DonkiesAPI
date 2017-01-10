import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import autoBind from 'react-autobind'
import { apiGetRequest, growlAddRequest } from 'actions'
import { apiCall4, ACCOUNTS_URL } from 'services/api'
import { createUUID } from 'services/helpers'
import { LoadingInline, SelectSimple } from 'components'



class BankRemove extends Component{
    constructor(props){
        super(props)
        autoBind(this)

        this.state = {
            accountId: null,
            isLoading: false
        }
    }

    /**
     * Options for SelectSimple
     */
    getOptions(accounts){
        let data = []
        data.push({value: '', text: '--- Select bank account'})
        
        for (let a of accounts){
            data.push({value: a.id, text: a.name})
        }
        return data
    }

    /**
     * Callback function, passed to SelectSimple
     */
    onSelectBank(value){
        if (value !== ''){
            this.setState({accountId: value})
        } else {
            this.setState({accountId: null})
        }
    }

    onClickRemove(){
        const { accountId } = this.state
        if (!accountId){
            return
        }
        this.submitRequest(accountId)
    }

    /**
     * Api request to remove bank account.
     */
    async submitRequest(accountId){
        this.setState({isLoading: true})

        const url = `${ACCOUNTS_URL}/${accountId}`

        let response = await apiCall4(url, true) 
        let member = await response.json()

        this.setState({isLoading: false})

        if (response.status === 200){
            // Update accounts and transactions
            this.props.apiGetRequest('accounts')
            this.props.apiGetRequest('transactions')
            this.props.onBankRemoved()            

        } else {
            const id = createUUID()
            this.props.growlAddRequest({
                id: id,
                message: 'Error',
                'type': 'danger'
            })
        }
    }

    render(){
        const { isLoading } = this.state
        const { accounts } = this.props
        const options = this.getOptions(accounts)

        if (isLoading){
            return <LoadingInline />
        }

        return (
            <div className="row">
                <div className="col-sm-6">
                    <SelectSimple
                        name="account"
                        onChange={this.onSelectBank}
                        options={options} />
                </div>

                <div className="col-sm-6">
                    <button
                        onClick={this.onClickRemove}
                        className="btn bgm-red btn-icon-text btn-sm waves-effect m-t-5">
                            <i className="zmdi zmdi-delete" />
                        {'Remove Account'}
                    </button>
                </div>

            </div>
        )
    }
}


BankRemove.propTypes = {
    accounts: PropTypes.array,
    apiGetRequest: PropTypes.func,
    growlAddRequest: PropTypes.func,
    onBankRemoved: PropTypes.func
}

const mapStateToProps = (state) => ({
    
})

export default connect(mapStateToProps, {
    apiGetRequest,
    growlAddRequest
})(BankRemove)