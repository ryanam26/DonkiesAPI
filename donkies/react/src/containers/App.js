import React, { Component, PropTypes } from 'react'
import { connect } from 'react-redux'
import { DragDropContext } from 'react-dnd'
import HTML5Backend from 'react-dnd-html5-backend'
import { Link, RouteHandler, Redirect } from 'react-router'
import Growl from 'services/Growl'

import {
    apiGetRequest,
    navigate,
    resetErrorMessage,
    updateRouterState } from 'actions'

import {
    Alert,
    Header,
    Footer,
    Loading,
    Sidebar } from 'components'


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
        this.props.apiGetRequest('settings')
        this.props.apiGetRequest('user')
        this.props.apiGetRequest('transactions')
        this.props.apiGetRequest('accounts')
    }

    
    componentWillReceiveProps(nextProps) {
        if(this.props.location.pathname !== nextProps.location.pathname){
            this.props.updateRouterState({
                pathname: nextProps.location.pathname,
                params  : nextProps.params
            })
        }

        // Growl global messages (come from Redux)
        if (this.props.growls !== nextProps.growls){
            for (let obj of nextProps.growls){
                const { message, ...settings } = obj
                let g = new Growl(message, settings)
                g.run()
            }
        }
    }

    componentWillUpdate(nextProps, nextState){
        if (nextProps.user && !nextProps.user.is_confirmed){
            this.props.navigate('/not_confirmed')
        }
    }

    handleChange(nextValue) {
        this.props.navigate(`/${nextValue}`)
    }

    render() {
        const {
            children,
            alerts,
            location,
            user } = this.props
        
        if (!user){
            return <Loading />    
        }

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

                <Footer />

            </wrap>
        )
    }
}

App.propTypes = {
    alerts: PropTypes.array,
    apiGetRequest: PropTypes.func,
    children: PropTypes.node, // Injected by React Router
    errorMessage: PropTypes.string,
    growls: PropTypes.array,
    location: PropTypes.object,
    navigate: PropTypes.func.isRequired,
    params: PropTypes.object,
    resetErrorMessage: PropTypes.func.isRequired,
    updateRouterState: PropTypes.func.isRequired,
    user: PropTypes.object
}


const mapStateToProps = (state) => ({
    alerts: state.alerts.data,
    errorMessage: state.errorMessage,
    growls: state.growl.data,
    user: state.user.item,
})


export default connect(mapStateToProps, {
    apiGetRequest,
    navigate,
    updateRouterState,
    resetErrorMessage,
})(App)


