import React, {Component, PropTypes} from 'react'
import autoBind from 'react-autobind'
import classNames from 'classnames'
import { SelectClean } from 'components'


/**
 * Data table component.
 * Props:
 *
 * data (required) - all data for rendering table.
 * searchFields - array of fields for search.
 *
 * data contains id, className, header (array of header names),
 * rows (array of tr objects), where each tr object
 * may contain "className", "onClick" function, "params" object for function and array of cols.
 * Each col object may contain "className", "onClick" function, "params", "colspan" and "value".
 */
class TableData extends Component{
    static get defaultProps() {
        return {
            isShowFooter: true,
            isShowSearch: true,
            searchFields: null
        }
    }

    constructor(props){
        super(props)
        autoBind(this)

        this.state = {
            perPage: 10
        }
    }

    onChangePerPage(value){
        this.setState({perPage: parseInt(value)})
    }

    getPerPageOptions(){
        let data = []
        data.push({value: '10', text: '10'})
        data.push({value: '25', text: '25'})
        data.push({value: '50', text: '50'})
        data.push({value: '100', text: '100'})
        return data
    }

    render(){
        const { data, isShowFooter, isShowSearch } = this.props
        
        return (
            <div className="card">
            <div className="table-responsive">
                <div className="dataTables_wrapper">
                    <div className="dataTables_length">
                        <label>
                            {'Show '}
                            <SelectClean
                                name="per_page"
                                options={this.getPerPageOptions()}
                                onChange={this.onChangePerPage} />
                            
                            {' entries'}
                        </label>
                    </div>

                    {isShowSearch &&
                        <div className="dataTables_filter">
                            <label>{'Search:'}
                                <input type="search" placeholder="Search..." />
                            </label>
                        </div>
                    }
                    

                    <table id={data.id} className="table table-striped dataTable">
                        <thead>
                            <tr>
                                {data.header.map((name, index) => {
                                    return <th key={index}>{name}</th>
                                })}
                            </tr>
                        </thead>

                        {isShowFooter &&
                            <tfoot>
                                <tr>
                                    {data.header.map((name, index) => {
                                        return <th key={index}>{name}</th>
                                    })}
                                </tr>
                            </tfoot>
                        }
                        
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

                <div className="dataTables_info">
                    {'Showing 1 to 10 of 57 entries'}
                </div>

                <div className="dataTables_paginate paging_simple_numbers">
                    <a className="paginate_button previous disabled">
                        {'Previous'}
                    </a>

                    <span>
                        <a className="paginate_button current">{'1'}</a>
                        <a className="paginate_button">{'2'}</a>
                    </span>

                    <a className="paginate_button next">{'Next'}</a>
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
    isShowFooter: PropTypes.bool,
    isShowSearch: PropTypes.bool,
    searchFields: PropTypes.array
}

export default TableData
