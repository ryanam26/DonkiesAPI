import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import autoBind from 'react-autobind'
import { TableData } from 'components'


class Transactions extends Component{
    constructor(props){
        super(props)
        autoBind(this)
    }

    render(){
        return (
            <wrap>
                <h3>{'Transactions'}</h3>
                <TableData />
            </wrap>
        )
    }
}


Transactions.propTypes = {
  
}

const mapStateToProps = (state) => ({
    
})

export default connect(mapStateToProps, {
  
})(Transactions)