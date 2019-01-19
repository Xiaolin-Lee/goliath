import React from 'react';
import InformationDialog from './InformationDialog'
import _ from 'lodash';
import PropTypes from 'prop-types';

class PersonalInventoryUpdateDialog extends React.Component {
    constructor(props){
        super(props);
        this.state = {
            show: props.show,
            options: [],
            selectedBrand: "",
            selectedCategory: "",
            selectedMerchandiseId: 0,
            price: 0,
            quantity: 0,
            deposit: false,
        };

        this.saveInventory = this.saveInventory.bind(this);
        this.cancelSave = this.cancelSave.bind(this);
        this.onChange = this.onChange.bind(this);
        this.onChangePrice = this.onChangePrice.bind(this);
        this.onChangeCount = this.onChangeCount.bind(this);
    }

    static propTypes = {
        show: PropTypes.bool,
        onCancel: PropTypes.func,
        currentUser: PropTypes.string
    };

    static getDerivedStateFromProps(props, state) {
        if (props.show !== state.show) {
            return {show: props.show};
        }
        return state;
    }

    onChange(selectedMerchandise) {
        this.setState({
            selectedBrand:selectedMerchandise.brand.brand,
            selectedCategory:selectedMerchandise.category.category,
            selectedMerchandiseId: selectedMerchandise.id,
        })
    }

    saveInventory() {
        console.log(this.state);
        (this.state.deposit ? 
        // 新增 
        $.post("/inventory/update/", {
            current_merchant_id: this.props.currentUser,
            merchandise_id: this.state.selectedMerchandiseId,
            quantity: this.state.quantity,
            price: this.state.price,
            remarks: "",
        })
        // 取出
        :$.post("/inventory/update/", {
            current_merchant_id: this.props.currentUser,
            merchandise_id: this.state.selectedMerchandiseId,
            quantity: this.state.quantity,
            deposit: this.state.deposit,
            remarks: "",
        })
        )
    }

    cancelSave() {
        this.setState({show: false});
        this.props.cancelSave();
    }

    onChangePrice(event) {
        this.setState( {price: event.target.value})
    }
    onChangeCount(event) {
        this.setState({quantity: event.target.value});
    }
    getDepositDialogBody() {
        return (<form className="fieldSection">
            <div className="item"><span>最新价格</span><input placeholder="最新价格"  value={this.state.price} onChange={this.onChangePrice} type="number" min="0"/></div>
            <div className="item"><span>新增数量</span><input placeholder="新增数量"  value={this.state.quantity} onChange={this.onChangeCount} type="number" min="0"/></div>
        </form>);
    }
    getWithdrawDialogBody() {
        return (<form className="fieldSection">
            <div className="item"><span>取出数量</span><input placeholder="取出数量"  value={this.state.quantity} onChange={this.onChangeCount} type="number" min="0"/></div>
        </form>);
    }
    render() {
        const saveDialogBody = this.state.deposit ? this.getDepositDialogBody() : this.getWithdrawDialogBody();
        return (<InformationDialog show={this.state.show}
                                   onConfirm={this.saveInventory}
                                   onCancel={this.cancelSave}
                                   body={saveDialogBody}
                                   title={this.state.deposit ? "新增商品库存" : "取出商品库存"} />);
    }
}

export default PersonalInventoryUpdateDialog