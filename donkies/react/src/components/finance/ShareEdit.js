import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import autoBind from 'react-autobind'
import { formToObject, getArraySum, isInteger } from 'services/helpers'


/**
 * Edit transfer_share of debt accounts.
 */ 
class ShareEdit extends Component{
    constructor(props){
        super(props)
        autoBind(this)

        this.state = {
            error: null
        }
    }

    /**
     * 1) All values in form should be integer.
     * 2) The sum of all values should be equal to 100.
     * Returns error or null if no error.
     */
    checkValues(form){
        for (let value of Object.values(form)){
            if (!isInteger(value)){
                return 'Please input only integer numbers.'
            }
        }
        
        let values = Object.values(form).map((num) => parseInt(num))

        if (getArraySum(values) !== 100){
            return 'The total sum of all share should be equal 100.'
        }
    }

    
    onChange(){
        let form = this.refs.form
        form = formToObject(form)
        let error = this.checkValues(form)
        if (error){
            this.setState({error: error})
        } else {
            this.setState({error: null})
        }
    }

    async submitRequest(form){

    }

    render(){
        const { accounts } = this.props
        const { error } = this.state

        return (
            <form ref="form">
            <div className="table-responsive">
                <table className="table table-condensed table-vmiddle">
                    <tbody>
                        {accounts.map((account, index) => {
                            return (
                                <tr key={index}>
                                    <td>{account.name}</td>
                                    <td>
                                        <input
                                            onChange={this.onChange}
                                            className="form-control input-sm"
                                            type="text"
                                            name={`id${account.id}`}
                                            defaultValue={account.transfer_share} />
                                    </td>
                                </tr>
                            )           
                        })}

                        <tr>
                            <td colSpan="2" className="text-right">
                                {error && <div className="error">{error}</div>}
                            </td>
                        </tr>


                    </tbody>
                </table>
            </div>
            </form>
        )
    }
}


ShareEdit.propTypes = {
    accounts: PropTypes.array
}

const mapStateToProps = (state) => ({
    
})

export default connect(mapStateToProps, {
  
})(ShareEdit)