import React, { Component, PropTypes } from 'react'
import autoBind from 'react-autobind'
import classNames from 'classnames'


/**
 * Base component for Inputs.
 * Has multiple versions.
 */
export default class InputBase extends Component {
    static get defaultProps() {
        return {
            type: 'text',
            col1: 'col-sm-4',
            col2: 'col-sm-8',
            disabled: false,
            errors: null,
            label: null,
            onBlur: null,
            onChange: null,
            onKeyDown: null,
            onKeyPress: null,
            onKeyUp: null,
            placeholder: null,
            style: {},
            zmdi: null,
            wrapperClass: 'form-group'
        }
    }

    constructor(props){
        super(props)
        autoBind(this)
        
        this.state = {
            inputClassName: 'fg-line',
            value: this.props.value
        }
    }

    componentWillReceiveProps(newProps){
        this.setState({value: newProps.value})
    }

    onFocus(e){
        this.setState({inputClassName: 'fg-line fg-toggled'})
    }

    onBlur(e){
        this.setState({inputClassName: 'fg-line'})

        if (this.props.onBlur){
            this.props.onBlur(e)
        }
    }

    onChange(e){
        this.setState({value: e.target.value})
        if (this.props.onChange){
            this.props.onChange(e)
        }
    }

    onKeyDown(e){
        if (this.props.onKeyDown){
            this.props.onKeyDown(e)
        }
    }

    onKeyPress(e){
        if (this.props.onKeyPress){
            this.props.onKeyPress(e)
        }
    }

    onKeyUp(e){
        if (this.props.onKeyUp){
            this.props.onKeyUp(e)
        }
    }

    hasError(){
        const {errors, name} = this.props
        return errors !== null && errors.hasOwnProperty(name)
    }

    renderErrors(){
        if (!this.hasError())
            return null

        const {errors, name} = this.props
        return (
            <wrap>
                {errors[name].map((item, index) => {
                    return <small key={index} className="help-block">{item}</small>
                })}
            </wrap>
        ) 
    }


    /**
     * Props for HTML input element.
     */
    getInputProps(){
        return {
            disabled: this.props.disabled,
            name: this.props.name,
            style: this.props.style,
            type: this.props.type,
            placeholder: this.props.placeholder,
            onFocus: this.onFocus,
            onBlur: this.onBlur,
            onChange: this.onChange,
            onKeyDown: this.onKeyDown,
            onKeyPress: this.onKeyPress,
            onKeyUp: this.onKeyUp
        }
    }

    renderVersion1(inputProps, cnWrapper){
        const { label, zmdi } = this.props
        const { inputClassName } = this.state

        return (
            <div className={cnWrapper}>
                {zmdi && 
                    <span className="input-group-addon">
                        <i className={`zmdi ${zmdi}`} />
                    </span>
                }
                
                <div className={inputClassName}>
                    {label &&
                        <label className="control-label">{label}</label>}

                    <input
                        className="form-control"
                        {...inputProps} />
                </div>

                {this.hasError() && this.renderErrors()}
            </div>
        )
    }

    renderVersion2(inputProps, cnWrapper){
        const { col1, col2, label } = this.props
        const cnCol1 = classNames('control-label', col1)

        return (
            <div className={cnWrapper}>
                <label className={cnCol1}>{label}</label>
                <div className={col2}>
                    <div className="fg-line">
                        <input
                            className="form-control input-sm"
                            {...inputProps} />
                    </div>

                    {this.hasError() && this.renderErrors()}
                </div>
            </div>
        )
    }

    render() {
        const { version, wrapperClass } = this.props
        const { value } = this.state
        let inputProps = this.getInputProps()
        
        // if controlled component
        if (this.props.value !== null && this.props.value !== undefined){
            inputProps.value = value
        }

        const cnWrapper = classNames(
            wrapperClass,
            {'has-error': this.hasError()}
        )

        if (version === 1){
            return this.renderVersion1(inputProps, cnWrapper)
        }

        if (version === 2){
            return this.renderVersion2(inputProps, cnWrapper)
        }

        // not reached
        return null
    }
}


InputBase.propTypes = {
    col1: PropTypes.string,
    col2: PropTypes.string,
    disabled: PropTypes.bool,
    errors: PropTypes.object,
    label: PropTypes.string,
    name: PropTypes.string.isRequired,
    onBlur: PropTypes.func,
    onChange: PropTypes.func,
    onKeyDown: PropTypes.func,
    onKeyPress: PropTypes.func,
    onKeyUp: PropTypes.func,
    placeholder: PropTypes.string,
    style: PropTypes.object,
    type: PropTypes.string,
    value: PropTypes.oneOfType([
        PropTypes.string,
        PropTypes.number
    ]),
    version: PropTypes.number,
    wrapperClass: PropTypes.string,
    zmdi: PropTypes.string
}
