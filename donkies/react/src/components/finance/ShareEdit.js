import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import autoBind from 'react-autobind'


/**
 * Edit transfer_share of debt accounts.
 */ 
class ShareEdit extends Component{
    constructor(props){
        super(props)
        autoBind(this)
    }

    render(){
        return (
            <div>{'ShareEdit'}</div>
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