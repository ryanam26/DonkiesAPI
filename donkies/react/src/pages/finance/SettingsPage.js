import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import autoBind from 'react-autobind'
import { CardSimple } from 'components'


class SettingsPage extends Component{
    constructor(props){
        super(props)
        autoBind(this)
    }

    render(){
        return (
            <div className="row">
                <div className="col-sm-6">
                    <CardSimple
                        header={'Unlink All Accounts \u0026 Refund All Change'}
                        headerClass="m-b-20"
                        isContentToBody={false}>

                        <button className="btn bgm-red btn-icon-text btn-sm waves-effect m-r-5">
                            <i className="zmdi zmdi-delete" />
                            {'Remove and Refund'}
                        </button>
                    </CardSimple>
                </div>

                <div className="col-sm-6">
                    <CardSimple
                        header="Setup Automatic Transfer to Debt Accounts"
                        headerClass="m-b-20"
                        isContentToBody={false}>
                        
                        <button className="btn bgm-lightblue btn-icon-text btn-sm waves-effect m-r-5">
                            <i className="zmdi zmdi-settings" />
                            {'Configure'}
                        </button>

                    </CardSimple>
                </div>
            </div>
        )
    }
}


SettingsPage.propTypes = {
}

const mapStateToProps = (state) => ({
})

export default connect(mapStateToProps, {
})(SettingsPage)

