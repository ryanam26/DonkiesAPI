import React, { Component, PropTypes } from 'react'
import { connect } from 'react-redux'
import { DragDropContext } from 'react-dnd'
import HTML5Backend from 'react-dnd-html5-backend'
import { Link, RouteHandler, Redirect } from 'react-router'


import {
    apiGetRequest,
    navigate,
    resetErrorMessage,
    updateRouterState } from 'actions'

import { Alert, Header, Footer, Sidebar } from 'components'


// @DragDropContext(HTML5Backend)
class App extends Component {
    constructor(props) {
        super(props)
        this.handleChange = this.handleChange.bind(this)
    }

    componentWillMount() {
        this.props.updateRouterState({
            pathname: this.props.location.pathname,
            params  : this.props.params
        })
    }

    
    componentWillReceiveProps(nextProps) {
        if(this.props.location.pathname !== nextProps.location.pathname){
            this.props.updateRouterState({
                pathname: nextProps.location.pathname,
                params  : nextProps.params
            })
        }
    }

    handleChange(nextValue) {
        this.props.navigate(`/${nextValue}`)
    }

    render() {
        const {
            children,
            alerts,
            location } = this.props
        
        return (
            <wrap>
                <Header />

                <section id="main">
                    <Sidebar />

                    <section id="content">
                        <div className="container">
                            {alerts.map((a, ind) => {
                              return <Alert key={ind} type={a.alertType} value={a.message} index={ind} showClose />  
                            })}

                            {children}
                        </div>
                    </section>
                </section>



            </wrap>
        )
    }
}

App.propTypes = {
    alerts: PropTypes.array,
    apiGetRequest: PropTypes.func,
    children: PropTypes.node, // Injected by React Router
    errorMessage: PropTypes.string,
    location: PropTypes.object,
    navigate: PropTypes.func.isRequired,
    params: PropTypes.object,
    resetErrorMessage: PropTypes.func.isRequired,
    updateRouterState: PropTypes.func.isRequired
}

function mapStateToProps(state) {
    return {
        alerts: state.alerts.data,
        errorMessage: state.errorMessage
    }
}


export default connect(mapStateToProps, {
    apiGetRequest,
    navigate,
    updateRouterState,
    resetErrorMessage,
})(App)


