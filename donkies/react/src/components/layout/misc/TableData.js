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
            currentPage: 1,
            perPage: 10
        }
    }

    componentWillReceiveProps(nextProps){
        this.setState({currentPage: 1})
    }

    onChangePerPage(value){
        this.setState({perPage: parseInt(value)})
    }

    onClickPage(num, e){
        e.preventDefault()
        this.setState({currentPage: num})
    }

    onClickNext(e){
        e.preventDefault()
        if (this.isNextActive()){
            this.setState({currentPage: this.state.currentPage + 1})    
        }
    }

    onClickPrevious(e){
        e.preventDefault()
        if (this.isPreviousActive()){
            this.setState({currentPage: this.state.currentPage - 1})    
        }
    }

    getPerPageOptions(){
        let data = []
        data.push({value: '10', text: '10'})
        data.push({value: '25', text: '25'})
        data.push({value: '50', text: '50'})
        data.push({value: '100', text: '100'})
        return data
    }

    isNextActive(){
        const { currentPage } = this.state
        if (currentPage < this.numPages()){
            return true
        }
        return false
    }

    isPreviousActive(){
        const { currentPage } = this.state
        if (currentPage > 1){
            return true
        }
        return false
    }

    numPages(){
        const num = this.totalRows() / this.state.perPage
        return Math.round(num)
    }

    /**
     * Returns array of numbers from 1 to numPages
     */
    numsArr(){
        let nums = []
        for (let i=1; i <= this.numPages(); i++){
            nums.push(i)
        }
        return nums
    }

    /** 
     * Active visible rows
     */ 
    rows(){
        const { data } = this.props
        const { currentPage, perPage } = this.state

        const ofs = (currentPage - 1) * perPage
        return data.rows.offset(ofs).limit(perPage)
    }

    /**
     * Returns the number of row "from"
     */
    showFrom(){
        const { currentPage, perPage } = this.state
        return (currentPage - 1) * perPage + 1
    }

    /**
     * Returns the number of row "to"
     */
    showTo(){
        const { currentPage, perPage } = this.state
        return currentPage * perPage
    }

    /**
     * Returns number of total rows
     */
    totalRows(){
        // TODO: apply search
        const { data } = this.props
        return data.rows.length
    }

    renderPagination(){
        const { currentPage } = this.state

        const cnNext = classNames(
            'paginate_button next',
            {'disabled': !this.isNextActive()}
        )
        const cnPrevious = classNames(
            'paginate_button previous',
            {'disabled': !this.isPreviousActive()}
        )

        return (
            <div className="dataTables_paginate paging_simple_numbers">
                <a
                    onClick={this.onClickPrevious}
                    className={cnPrevious}>{'Previous'}</a>

                <span>
                    {this.numsArr().map((num) => {
                        const cn = classNames(
                            'paginate_button',
                            {'current': num === currentPage}
                        )
                        return (
                            <a
                                onClick={this.onClickPage.bind(null, num)}
                                key={num}
                                className={cn}>{num}</a>
                        )

                    })}
                </span>

                <a
                    onClick={this.onClickNext}
                    className={cnNext}>{'Next'}</a>
            </div>
        )
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
                            {this.rows().map((row, index) => {
                                const f = row.onClick ? row.onClick.bind(null, row.params) : null

                                return (
                                    <tr key={index} className={row.className} onClick={f}>
                                        {row.cols.map((col, index) => {
                                            
                                            let colspan = col.colspan ? col.colspan : 1
                                            const f = col.onClick ? col.onClick.bind(null, col.params) : null
                                            const oddEven = (index + 1) % 2 === 0 ? 'even' : 'odd'
                                            const cn = classNames(col.className, oddEven)

                                            return (
                                                <td colSpan={colspan} key={index} className={cn} onClick={f}>
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
                    {`Showing ${this.showFrom()} to ${this.showTo()} of ${this.totalRows()} entries`}
                </div>

                {this.renderPagination()}

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
