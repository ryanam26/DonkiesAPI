import React, {Component, PropTypes} from 'react'
import classNames from 'classnames'

class ErrorBlock extends Component{
    constructor(props){
        super(props)
    }

    render(){
        const errors = this.props.errors

        if (errors === null || !errors.hasOwnProperty('non_field_errors'))
            return null

        return (

            <div className="custom-errors">
                <ul>
                   {errors.non_field_errors.map( (e, index) => {
                        return <li key={index}>{e}</li>
                   })}
                </ul>
            </div>
        )
    }
}


ErrorBlock.propTypes = {
    errors: PropTypes.object
}

export default ErrorBlock
