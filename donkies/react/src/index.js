// Should be first line
import { AppContainer } from 'react-hot-loader'

import 'babel-polyfill'
import React from 'react'
import { render } from 'react-dom'


import { history } from 'services'
import routes from 'routes'
import Root from 'containers/Root'
import configureStore from 'store/configureStore'
import rootSaga from 'sagas'

const store = configureStore(window.__INITIAL_STATE__)
store.runSaga(rootSaga)


render(
    <AppContainer>
        <Root
            history={history}
            routes={routes}
            store={store} />
    </AppContainer>,
    document.getElementById('root')
)

if (module.hot) {
    module.hot.accept('./containers/Root', () => {
        const Next = require('./containers/Root').default
        render(
            <AppContainer>
                <Next
                    history={history}
                    routes={routes}
                    store={store} /> 
            </AppContainer>,
            document.getElementById('root'));
    });
}
