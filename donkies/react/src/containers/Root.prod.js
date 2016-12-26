import React, { Component, PropTypes } from 'react'
import { Provider } from 'react-redux'
import { Router, RouterContext } from 'react-router'

export default class Root extends Component {
  render() {
    const { store, history, routes, type, renderProps } = this.props

    return (
      <Provider store={store}>
        {type === 'server'
          ? <RouterContext {...renderProps} />
          : <Router history={history} routes={routes} />
        }
      </Provider>
    )
  }
}

Root.propTypes = {
  history: PropTypes.object.isRequired,
  renderProps: PropTypes.func,
  routes: PropTypes.node.isRequired,
  store: PropTypes.object.isRequired,
  type: PropTypes.string
}