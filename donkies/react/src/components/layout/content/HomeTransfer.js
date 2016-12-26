import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import autoBind from 'react-autobind'


class HomeTransfer extends Component{
    constructor(props){
        super(props)
        autoBind(this)
    }

    render(){
        const content = 'This is the amount that is available for transfer since the last time you transfered to your debt accounts.'
        const title = 'Available For Transfer'
        const text = 'Available For Transfer'
        const amount = '$ 458,778'
        const btnText = 'Transfer Now'

        return (
            <div className="row">
                <div className="col-sm-6 col-sm-offset-3">
                    <div
                        className="mini-charts-group-transfer" data-trigger="hover" data-toggle="popover"
                        data-placement="top"
                        data-content={content}
                        title=""
                        data-original-title={title}>
                        
                        <div className="mini-charts-item bgm-orange">
                            <div className="clearfix">
                                <div className="chart stats-line" />
                                <div className="count">
                                    <small>{text}</small>
                                    <h2>{amount}</h2>
                                </div>
                            </div>
                        </div>
                        
                        <div className="mini-charts-group-addon">
                            <button className="btn bgm-gray waves-effect">
                                {btnText}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        )
    }
}


HomeTransfer.propTypes = {
}

const mapStateToProps = (state) => ({
})

export default connect(mapStateToProps, {
})(HomeTransfer)