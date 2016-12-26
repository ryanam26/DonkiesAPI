import React, {Component, PropTypes} from 'react'
import autoBind from 'react-autobind'
import classNames from 'classnames'


export default class Input extends Component {
    static get defaultProps() {
        return {
            type: 'text',
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
            zmdi: null
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

    render() {
        const { 
            disabled,
            name,
            label,
            style,
            type,
            placeholder,
            wrapperClass,
            zmdi } = this.props
        const { value, inputClassName } = this.state
        
        let inputProps = {
            disabled,
            name,
            style,
            type,
            placeholder,
            onFocus: this.onFocus,
            onBlur: this.onBlur,
            onChange: this.onChange,
            onKeyDown: this.onKeyDown,
            onKeyPress: this.onKeyPress,
            onKeyUp: this.onKeyUp
        }
        
        // if controlled component
        if (this.props.value !== null && this.props.value !== undefined){
            inputProps.value = value
        }

        const wrapperCN = classNames(
            wrapperClass,
            {'has-error': this.hasError()}
        )

        return (
            <div className={wrapperCN}>
                {zmdi && 
                    <span className="input-group-addon">
                        <i className={`zmdi ${zmdi}`} />
                    </span>
                }
                
                <div className={inputClassName}>
                    {label &&
                        <label className="control-label">{label}</label>}

                    <input
                        type="text"
                        className="form-control"
                        {...inputProps} />
                </div>

                {this.hasError() && this.renderErrors()}
            </div>
        )
    }
}


Input.propTypes = {
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
    wrapperClass: PropTypes.string.isRequired,
    zmdi: PropTypes.string
}
