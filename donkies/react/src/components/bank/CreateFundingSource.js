import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import autoBind from 'react-autobind'
import { navigate } from 'actions'
import { apiCall3, GET_IAV_TOKEN_URL } from 'services/api'
import { DWOLLA_MODE } from 'store/configureStore'
import { LoadingInline } from 'components'


/**
 * Component's flow.
 *
 * On component init get "account" from "GET" params,
 * check account and if account passes all checks,
 * send request to get iav token from API,
 * and set iav token to state.
 *
 * On click button, send request using dwolla.js
 * and dwolla generates flow in div id=iavContainer in iframe.
 * After processing user's input, dwolla will send 
 * result and error in callback.
 * If success, dwolla will give JSON with link to created funding_source.
 * Send request to API to save funding_source in database.
 */
class CreateFundingSource extends Component{
    constructor(props){
        super(props)
        autoBind(this)

        this.state = {
            account: null,
            error: null,
            iavToken: null
        }
    }

    componentWillMount(){
        this.init(this.props)   
    }

    componentDidMount(){
        dwolla.configure(DWOLLA_MODE)   
    }

    componentWillReceiveProps(nextProps){
        this.init(nextProps)
    }

    init(props){
        const { account } = this.state
        if (account){
            return
        }

        const { user, accounts, location } = props
        if (!user || !accounts){
            return
        }

        const a = this.getAccount(accounts, location)
        this.setState({account: a})
        const result = this.checkAccount(a, user)
        if (result){
            this.getIAVTokenRequest()    
        }
    }

    onClickStart(){
        const { iavToken } = this.state

        dwolla.configure('uat')
        dwolla.iav.start(
            iavToken, 
            {
                container: 'iavContainer',
                // stylesheets: ['http://donkies.co/css/custom-dwolla.css']
            },
        (err, res) => {
            if (err === null){
                const href = res['_links']['funding-source']['href']
                // send to server href, account, prepare API endpoint
            }
        })
    }

    /**
     * Validates account for possibility create in Dwolla.
     *
     * 1) Account should be debit.
     * 2) Account not created yet in Dwolla. 
     * 3) Type should be CHECKING or SAVINGS.
     * 4) User should have dwolla_customer.dwolla_id
     * 5) dwolla_customer should be verified.
     */
    checkAccount(account, user){
        const { navigate } = this.props

        if (account.type_ds !== 'debit'){
            this.setState({
                error: 'You can not use Debt account as funding source.'
            })
            return false
        }

        if (account.is_dwolla_created){
            navigate('/accounts')
            return false  
        }

        if (!['CHECKING', 'SAVINGS'].includes(account.type)){
            this.setState({
                error: 'You can not use this account as funding source. The account type should be Checking or Savings.'
            })
            return false
        }

        if (!user.dwolla_customer.dwolla_id){
            this.setState({
                error: 'Customer is not yet created in Dwolla.'
            })
            return false
        }

        if (user.dwolla_customer.status !== 'verified'){
            this.setState({
                error: 'Customer is not yet verified in Dwolla.'
            })   
            return false
        }
        return true
    }

    /**
     * Get account by "GET" param or redirect to /accounts page.
     */
    getAccount(accounts, location){
        const { navigate } = this.props
        if (location.query.hasOwnProperty('account_uid')){
            const uid = location.query.account_uid
            for (let account of accounts){
                if (account.uid === uid){
                    return account
                }
            }
        }
        navigate('/accounts')
    }

    async getIAVTokenRequest(){
        const { user } = this.props
        const url = `${GET_IAV_TOKEN_URL}/${user.dwolla_customer.dwolla_id}`  
        const data = {}
        let response = await apiCall3(url, data, true)
        if (response.status === 500){
            this.setState({error: 'Server error.'})
            return
        }

        const result = await response.json()
        if (response.status === 200){
            this.setState({iavToken: result.token})
        } else if (response.status === 400){
            this.setState({error: result.message})
        }
    }

    renderIAV(){
        const { iavToken } = this.state
        if (!iavToken){
            return <LoadingInline />
        }

        return (
            <wrap>
                <div id="mainContainer">
                    <button
                        className="btn btn-primary btn-sm waves-effect"
                        onClick={this.onClickStart}>
                        {'Create funding source'}
                    </button>
                </div>  

                <div id="iavContainer" />
            </wrap>
        )
    }

    render(){
        const { account, error, iavToken } = this.state

        if (!account){
            return <LoadingInline />
        }

        return (
            <wrap>
                <h3>{account.name}{': create funding source'}</h3>

                {error ? 
                    <div className="custom-error">{error}</div>
                :
                    this.renderIAV()
                }
            </wrap>
        )
    }
}


CreateFundingSource.propTypes = {
    accounts: PropTypes.array,
    location: PropTypes.object,
    navigate: PropTypes.func,
    user: PropTypes.object
}

const mapStateToProps = (state) => ({
    accounts: state.accounts.debitAccounts,
    user: state.user.item
})

export default connect(mapStateToProps, {
    navigate
})(CreateFundingSource)