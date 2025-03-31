import axios from 'axios';
import { INVENTORY_API } from './config';

export const createInventoryProduct = (formData) => {
  return axios.post(`${INVENTORY_API}/inventoryproduct/`, formData);
};

export const getInventoryProducts = () => {
  return axios.get(`${INVENTORY_API}/inventoryproduct/`);
};
export const updateInventoryProduct = (productId, updatedProduct) => {
  return axios.put(`${INVENTORY_API}/inventoryproduct/${productId}`, updatedProduct);
};

