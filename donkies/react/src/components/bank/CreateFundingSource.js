import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import autoBind from 'react-autobind'
import { navigate } from 'actions'
import { DWOLLA_MODE } from 'store/configureStore'


class CreateFundingSource extends Component{
    constructor(props){
        super(props)
        autoBind(this)
    }

    componentDidMount(){
        dwolla.configure(DWOLLA_MODE)   
    }

    onClickStart(){
        let iavToken = '4adF858jPeQ9RnojMHdqSD2KwsvmhO7Ti7cI5woOiBGCpH5krY'
        dwolla.configure('uat')
        dwolla.iav.start(iavToken, 'iavContainer', (err, res) => {
            console.log(' -- Response: ' + JSON.stringify(res))
            console.log(' -- Error: ' + JSON.stringify(err))
        })
    }

    getAccount(){
        const { accounts, location, navigate } = this.props
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

    render(){
        const { accounts } = this.props
        
        if (!accounts){
            return null
        }

        const account = this.getAccount()
        console.log(account)

        return (
            <wrap>
                <h3>{account.name}{': create funding source'}</h3>

                <div id="mainContainer">
                    <input
                        onClick={this.onClickStart}
                        type="button"
                        value="Create funding source" />
                </div>  

                <div id="iavContainer" />

            </wrap>
        )
    }
}


CreateFundingSource.propTypes = {
    accounts: PropTypes.array,
    location: PropTypes.object,
    navigate: PropTypes.func
}

const mapStateToProps = (state) => ({
    accounts: state.accounts.debitAccounts,
})

export default connect(mapStateToProps, {
    navigate
})(CreateFundingSource)