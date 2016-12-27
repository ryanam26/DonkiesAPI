import React, {Component, PropTypes} from 'react'
import autoBind from 'react-autobind'
import classNames from 'classnames'
import InputBase from './InputBase'


export default function(props){
    return (
        <InputBase version={2} {...props} />
    )
}
