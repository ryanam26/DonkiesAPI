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





























