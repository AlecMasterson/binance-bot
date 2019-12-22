import API from './AppAPI';

export default class BaseAPI {
    static async getData(endpoint) {
        return await API.get(endpoint)
            .then((response) => {
                return {
                    error: false,
                    data: response.data
                };
            })
            .catch((error) => {
                return {
                    error: true,
                    data: null
                };
            });
    }
}