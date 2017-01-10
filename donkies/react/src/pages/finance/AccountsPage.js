import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import autoBind from 'react-autobind'
import { Link } from 'react-router'
import { BankAccounts, CardSimple } from 'components'



export default class AccountsPage extends Component{
    constructor(props){
        super(props)
        autoBind(this)
    }

    render(){
        return (
            <div className="row">
                <div className="col-sm-6">
                    <BankAccounts />
                </div>

                <div className="col-sm-6">
                    <CardSimple
                        header="Lenders"
                        headerClass="m-b-20"
                        isContentToBody={false}>
                        
                        <button className="btn bgm-lightblue btn-icon-text btn-sm waves-effect m-r-5">
                            <i className="zmdi zmdi-plus" />
                            {'Add Lender '}
                        </button>

                        <button className="btn bgm-red btn-icon-text btn-sm waves-effect m-r-5">
                            <i className="zmdi zmdi-delete" />
                            {'Remove Lender'}
                        </button>
                        
                    </CardSimple>
                </div>
            </div>

        )
    }
}


AccountsPage.propTypes = {
}
