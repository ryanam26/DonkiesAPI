import React, {Component, PropTypes} from 'react'
import { connect } from 'react-redux'
import autoBind from 'react-autobind'
import {
    CardSimple,
    HomeMiniCharts,
    HomeTransfer,
    TableSimple } from 'components'


export default class HomePageComponent extends Component{
    constructor(props){
        super(props)
        autoBind(this)
    }

    /**
     * TODO: Get data to table from API.
     */
    getTransactionsData(){
        let mock = [
            ['12/17/2016', 'Starbucks', '$5.21', '$0.79'],
            ['12/16/2016', 'Mc Donalds', '$7.45', '$0.55']
        ]


        let data = {}
        data.id = 'transactions'
        data.header = ['DATE', 'DESCRIPTION', 'TRANSACTION AMOUNT', 'ROUND UP']
        data.rows = []

        for (let arr of mock){
            let row = {}
            row.cols = []
            let count = 0
            for (let s of arr){
                let col = {value: s}
                col.className = count === 1 ?  '' : 'f-500 c-cyan'
                row.cols.push(col)
                count++
            }
            data.rows.push(row)
        }
        return data
    }

    render(){
        return (
            <wrap>
                <HomeMiniCharts />
                <HomeTransfer />

                <CardSimple
                    header="Transactions"
                    smallHeader="This will show the most recent transactions">

                    <TableSimple data={this.getTransactionsData()} />
                </CardSimple>
            </wrap>
        )
    }
}

HomePageComponent.propTypes = {
}
