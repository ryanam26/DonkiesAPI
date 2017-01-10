import React, {Component, PropTypes} from 'react'
import classNames from 'classnames'


/**
 * Data table component.
 * Props:
 *
 * onSearchChange - (optional) if passed, show search block.
 * data (required) - all data for rendering table.
 *
 * data contains id, className, header (array of header names),
 * rows (array of tr objects), where each tr object
 * may contain "className", "onClick" function, "params" object for function and array of cols.
 * Each col object may contain "className", "onClick" function, "params", "colspan" and "value".
 */
class TableData extends Component{
    constructor(props){
        super(props)
    }

    render(){
        const { data, onSearchChange } = this.props
        
        return (
            <div className="card">
            <div className="table-responsive">
                <div id="data-table-basic_wrapper" className="dataTables_wrapper">
                    <div className="dataTables_length">
                        <label>
                            {'Show '}
                            <select>
                                <option value="10">{'10'}</option>
                                <option value="25">{'25'}</option>
                                <option value="50">{'50'}</option>
                                <option value="100">{'100'}</option>
                            </select>
                            {' entries'}
                        </label>
                    </div>

                    <div id="data-table-basic_filter" className="dataTables_filter">
                        <label>{'Search:'}
                            <input type="search" placeholder="Search..." aria-controls="data-table-basic" />
                        </label>
                    </div>

                    <table
                        id="data-table-basic"
                        className="table table-striped dataTable"
                        role="grid"
                        aria-describedby="data-table-basic_info">
                        
                        <thead>
                            <tr role="row">
                                <th
                                    className="sorting_asc"aria-controls="data-table-basic"
                                    rowSpan="1"
                                    colSpan="1"
                                    aria-sort="ascending">
                                    {'Col1'}
                                </th>

                                <th
                                    className="sorting_asc"aria-controls="data-table-basic"
                                    rowSpan="1"
                                    colSpan="1"
                                    aria-sort="ascending">
                                    {'Col2'}
                                </th>
                            </tr>
                        </thead>

                    <tfoot>
                        <tr>
                            <th rowSpan="1" colSpan="1">{'Col1'}</th>
                            <th rowSpan="1" colSpan="1">{'Col2'}</th>
                        </tr>
                    </tfoot>
                    <tbody>
                    
                        <tr role="row" className="odd">
                            <td className="sorting_1">Airi Satou</td>
                            <td>Accountant</td>
                        </tr>

                        <tr role="row" className="even">
                            <td className="sorting_1">Angelica Ramos</td>
                            <td>Chief Executive Officer (CEO)</td>
                        </tr>

                    </tbody>
                </table>

                <div
                    className="dataTables_info"
                    id="data-table-basic_info"
                    role="status" aria-live="polite">

                    {'Showing 1 to 10 of 57 entries'}
                </div>

                <div
                    className="dataTables_paginate paging_simple_numbers"
                    id="data-table-basic_paginate">
                    <a
                        className="paginate_button previous disabled"
                        aria-controls="data-table-basic"
                        data-dt-idx="0"
                        id="data-table-basic_previous">{'Previous'}</a>

                    <span>
                        <a
                            className="paginate_button current"
                            aria-controls="data-table-basic"
                            data-dt-idx="1">{'1'}</a>

                        <a
                            className="paginate_button "
                            aria-controls="data-table-basic"
                            data-dt-idx="2">{'2'}</a>

                            
                    </span>

                    <a
                        className="paginate_button next"
                        aria-controls="data-table-basic"
                        data-dt-idx="7"
                        id="data-table-basic_next">{'Next'}</a>
                </div>

            </div>
        </div>
        </div>
            
        )
    }
}


TableData.propTypes = {
    data: PropTypes.shape({
        id: PropTypes.string,
        className: PropTypes.string,
        header: PropTypes.arrayOf(PropTypes.string),
        rows: PropTypes.arrayOf(
            PropTypes.shape({
                className: PropTypes.string,
                onClick: PropTypes.func,
                params: PropTypes.object,
                cols: PropTypes.arrayOf(
                    PropTypes.shape({
                        colspan: PropTypes.number,
                        className: PropTypes.string,
                        onClick: PropTypes.func,
                        params: PropTypes.object,
                        value: PropTypes.any
                    })
                )
            })
        )
    }),
    onSearchChange: PropTypes.func,
}

export default TableData




/*
<div>
    {onSearchChange ?
        <div className="col-lg-4 col-lg-offset-8" style={{marginBottom: 10}}>
            <div className="form-control-wrapper form-control-icon-right">
                <input
                    onChange={onSearchChange}
                    type="text"
                    className="form-control form-control-rounded"
                    placeholder="Search..."/>
                <i className="font-icon font-icon-search" />
            </div>
        </div> : null}
    
    <div className="table-responsive">
        <table id={data.id} className={data.className}>
            {data.header !== null ?
                <thead>
                    <tr>
                        {data.header.map((name, index) => {
                            return <th key={index}>{name}</th>
                        })}
                    </tr>
                </thead> : null}
            
            <tbody>
                {data.rows.map((row, index) => {
                    const f = row.onClick ? row.onClick.bind(null, row.params) : null

                    return (
                        <tr key={index} className={row.className} onClick={f}>
                            {row.cols.map((col, index) => {
                                let colspan = col.colspan ? col.colspan : 1

                                const f = col.onClick ? col.onClick.bind(null, col.params) : null

                                return (
                                    <td colSpan={colspan} key={index} className={col.className} onClick={f}>
                                        {col.value}
                                    </td>
                                )
                            })}
                        </tr>
                    )
                })}
            </tbody>
        </table>
    </div>
</div>
*/

















