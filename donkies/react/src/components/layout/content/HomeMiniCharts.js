import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import autoBind from 'react-autobind'
import classNames from 'classnames'


class HomeMiniCharts extends Component{
    constructor(props){
        super(props)
        autoBind(this)
    }

    /**
     * TODO: GET this data from API.
     */
    getData(){
        let arr = []

        arr.push({
            content: 'This is the total amount that has been rounded up since registering with the app.',
            title: 'Total Round Up',
            colorClass: 'bgm-lightgreen',
            statClass: 'stats-line',
            text: 'Total Round Up',
            number: '987,459'

        })

        arr.push({
            content: 'This is the amount that has been transfered and applied to your debt accounts since registering with the app.',
            title: 'Total Transfered',
            colorClass: 'bgm-purple',
            statClass: 'stats-bar-2',
            text: 'Total Transfered',
            number: '356,785K'

        })

        arr.push({
            content: 'This is the amount of payments saved since registered with the app.',
            title: 'Payments saved',
            colorClass: 'bgm-bluegray',
            statClass: 'stats-line-2',
            text: 'Payments Saved',
            number: '23'

        })

        return arr
    }

    render(){

        const data = this.getData()

        return (
            <div className="mini-charts">
                <div className="row">
                    {data.map((obj, index) => {
                        const colorClass = classNames('mini-charts-item', obj.colorClass)
                        const statClass = classNames('chart', obj.statClass)

                        return (
                            <div
                                key={index}
                                className="col-sm-6 col-md-4" data-trigger="hover" data-toggle="popover"
                                data-placement="top"
                                data-content={obj.content}
                                title=""
                                data-original-title={obj.title}>
                                
                                <div className={colorClass}>
                                    <div className="clearfix">
                                        <div className={statClass} />
                                        <div className="count">
                                            <small>{obj.text}</small>
                                            <h2>{obj.number}</h2>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )                    
                    })}

                    
                </div>
            </div>
        )
    }
}


HomeMiniCharts.propTypes = {
}

const mapStateToProps = (state) => ({
})

export default connect(mapStateToProps, {
})(HomeMiniCharts)

