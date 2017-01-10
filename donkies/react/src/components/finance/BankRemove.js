import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import autoBind from 'react-autobind'


class BankRemove extends Component{
    constructor(props){
        super(props)
        autoBind(this)
    }

    render(){
        return (
            <wrap>
            <select className="form-control">
                <option>Select an Option</option>
                <option>Option 1</option>
                
            </select>
            </wrap>
        )
    }
}


BankRemove.propTypes = {
    
}

const mapStateToProps = (state) => ({
    
})

export default connect(mapStateToProps, {
  
})(BankRemove)