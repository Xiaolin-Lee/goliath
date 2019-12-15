import React from 'react';
import ReactTable from "react-table";

export default class InventoryTable extends React.Component{
    constructor(props) {
        super(props);
        this.state = {
            inventories: props.data,
            columns: props.columns,
            className: props.className,
            pageIndex: props.page,
        };
    }

    static getDerivedStateFromProps(nextProps, prevState) {
        if (nextProps.data !== prevState.inventories) {
            return ({ inventories: nextProps.data});
        }
        return ({prevState});
    }

    getRowWidth(width) {
        return width || 100;
    }

    getTitle() {
        return  _.map(this.state.columns, (column) => {
            const width = this.getRowWidth(column.width)
            if (column.type === "text")
           {
               return {
                   Header: column.title,
                   accessor: column.selector,
                   width: width
               }
           }
           if (column.type === "action") {
               return {
                   Header: column.title,
                   accessor: column.selector,
                   Cell: (row) => column.renderContent(row)
               }
           }
        });
    }

    render() {
        return <ReactTable data={this.state.inventories}
                           columns={this.getTitle()}
                           className="-striped -highlight"
                           filterable={true}
                           showPagination={this.props.showPagination}
                           manual={this.props.manual}
                           pages={this.props.pages}
                           page={this.state.pageIndex}
                           pageSize={this.props.pageSize}
                           onFetchData={this.props.onFetchData}
        />
    }
};
