import React, {useState, useEffect} from 'react';
import TagsInput from 'react-tagsinput';
import 'react-tagsinput/react-tagsinput.css';
import Dropzone from 'react-dropzone'
import axios from 'axios';


const CreateProduct = (props) => {

    const [productVariantPrices, setProductVariantPrices] = useState([])

    const [productVariants, setProductVariant] = useState([
        {
            option: 1,
            tags: []
        }
    ])

    const [productImage, setProductImage] = useState(null)
    const [productDetails, setProductDetails] = useState({})

    const fetchProductData = () => {
        axios({
            url: `/product/api/details/${props.product_id}/`,
            method: "get",
        })
            .then((res) => {
                console.log(res)
                setProductVariantPrices(res.data.product_variant_prices);
                setProductVariant(res.data.product_variants);
                setProductDetails(res.data.product_details);
            })
            .catch((err) => console.error(err));
    };

    useEffect(() => {
        if (props.is_for_update == "true") {
            fetchProductData();
        }
    }, [props.is_for_update]);
    
    console.log(typeof props.variants)
    // handle click event of the Add button
    const handleAddClick = () => {
        let all_variants = JSON.parse(props.variants.replaceAll("'", '"')).map(el => el.id)
        let selected_variants = productVariants.map(el => el.option);
        let available_variants = all_variants.filter(entry1 => !selected_variants.some(entry2 => entry1 == entry2))
        setProductVariant([...productVariants, {
            option: available_variants[0],
            tags: []
        }])
    };

    const onProductDetailChange = (event) => {
        const { name, value } = event.target;
        setProductDetails((prevS) => {
            return {
                ...prevS,
                [name]: value,
            };
        });
    };

    // handle input change on tag input
    const handleInputTagOnChange = (value, index) => {
        let product_variants = [...productVariants]
        product_variants[index].tags = value
        setProductVariant(product_variants)

        checkVariant()
    }

    // remove product variant
    const removeProductVariant = (index) => {
        let product_variants = [...productVariants]
        product_variants.splice(index, 1)
        setProductVariant(product_variants)
    }

    // check the variant and render all the combination
    const checkVariant = () => {
        let tags = [];

        productVariants.filter((item) => {
            tags.push(item.tags)
        })

        setProductVariantPrices([])

        getCombn(tags).forEach(item => {
            setProductVariantPrices(productVariantPrice => [...productVariantPrice, {
                title: item,
                price: 0,
                stock: 0
            }])
        })

    }

    // combination algorithm
    function getCombn(arr, pre) {
        pre = pre || '';
        if (!arr.length) {
            return pre;
        }
        let ans = arr[0].reduce(function (ans, value) {
            return ans.concat(getCombn(arr.slice(1), pre + value + '/'));
        }, []);
        return ans;
    }

    const onProductVariantPriceChange = (event, productVariantTitle) => {
        const { name, value } = event.target;

        setProductVariantPrices((prevS) => {
            return prevS.map((pV) =>
                pV.title === productVariantTitle ? { ...pV, [name]: value } : pV
            );
        });
    };

    // Save product
    let saveProduct = (event) => {
        event.preventDefault();
        // TODO : write your code here to save the product
        let formData = new FormData();

        formData.append("product_details", JSON.stringify(productDetails));
        productImage && formData.append("product_image", productImage[0]);
        formData.append("product_variants", JSON.stringify(productVariants));
        formData.append(
            "product_variant_prices",
            JSON.stringify(productVariantPrices)
        );

        if (props.is_for_update == "true") {
            axios({
                url: `/product/api/update/${props.product_id}/`,
                method: "put",
                data: formData,
                headers: {
                    "Content-Type": "multipart/form-data",
                },
            })
                .then((res) => {
                    window.location.href = "/product/list/";
                })
                .catch((err) => console.error(err));
        } else {
            axios({
                url: "/product/api/create/",
                method: "post",
                data: formData,
                headers: {
                    "Content-Type": "multipart/form-data",
                },
            })
                .then((res) => {
                    window.location.href = "/product/list/";
                })
                .catch((err) => console.error(err));
        }  
    };


    return (
        <div>
            <section>
                <div className="row">
                    <div className="col-md-6">
                        <div className="card shadow mb-4">
                            <div className="card-body">
                                <div className="form-group">
                                    <label htmlFor="">Product Name</label>
                                    <input name="title" type="text" placeholder="Product Name" className="form-control" value={productDetails.title} onChange={onProductDetailChange}/>
                                </div>
                                <div className="form-group">
                                    <label htmlFor="">Product SKU</label>
                                    <input name="sku" type="text" placeholder="Product SKU" className="form-control" value={productDetails.sku} onChange={onProductDetailChange}/>
                                </div>
                                <div className="form-group">
                                    <label htmlFor="">Description</label>
                                    <textarea name="description" id="" cols="30" rows="4" className="form-control" value={productDetails.description} onChange={onProductDetailChange}></textarea>
                                </div>
                            </div>
                        </div>

                        <div className="card shadow mb-4">
                            <div
                                className="card-header py-3 d-flex flex-row align-items-center justify-content-between">
                                <h6 className="m-0 font-weight-bold text-primary">Media</h6>
                            </div>
                            <div className="card-body border">
                                <Dropzone onDrop={acceptedFiles => setProductImage(acceptedFiles)}>
                                    {({getRootProps, getInputProps}) => (
                                        <section>
                                            <div {...getRootProps()}>
                                                <input {...getInputProps()} />
                                                <p>Drag 'n' drop some files here, or click to select files</p>
                                            </div>
                                        </section>
                                    )}
                                </Dropzone>
                            </div>
                        </div>
                    </div>

                    <div className="col-md-6">
                        <div className="card shadow mb-4">
                            <div
                                className="card-header py-3 d-flex flex-row align-items-center justify-content-between">
                                <h6 className="m-0 font-weight-bold text-primary">Variants</h6>
                            </div>
                            <div className="card-body">

                                {
                                    productVariants.map((element, index) => {
                                        return (
                                            <div className="row" key={index}>
                                                <div className="col-md-4">
                                                    <div className="form-group">
                                                        <label htmlFor="">Option</label>
                                                        <select className="form-control" defaultValue={element.option}>
                                                            {
                                                                JSON.parse(props.variants.replaceAll("'", '"')).map((variant, index) => {
                                                                    return (<option key={index}
                                                                                    value={variant.id}>{variant.title}</option>)
                                                                })
                                                            }

                                                        </select>
                                                    </div>
                                                </div>

                                                <div className="col-md-8">
                                                    <div className="form-group">
                                                        {
                                                            productVariants.length > 1
                                                                ? <label htmlFor="" className="float-right text-primary"
                                                                         style={{marginTop: "-30px"}}
                                                                         onClick={() => removeProductVariant(index)}>remove</label>
                                                                : ''
                                                        }

                                                        <section style={{marginTop: "30px"}}>
                                                            <TagsInput value={element.tags}
                                                                       style="margin-top:30px"
                                                                       onChange={(value) => handleInputTagOnChange(value, index)}/>
                                                        </section>

                                                    </div>
                                                </div>
                                            </div>
                                        )
                                    })
                                }


                            </div>
                            <div className="card-footer">
                                {productVariants.length !== 3
                                    ? <button className="btn btn-primary" onClick={handleAddClick}>Add another
                                        option</button>
                                    : ''
                                }

                            </div>

                            <div className="card-header text-uppercase">Preview</div>
                            <div className="card-body">
                                <div className="table-responsive">
                                    <table className="table">
                                        <thead>
                                        <tr>
                                            <td>Variant</td>
                                            <td>Price</td>
                                            <td>Stock</td>
                                        </tr>
                                        </thead>
                                        <tbody>
                                        {
                                            productVariantPrices.map((productVariantPrice, index) => {
                                                return (
                                                    <tr key={index}>
                                                        <td>{productVariantPrice.title}</td>
                                                        <td><input name="price" onChange={(e) => onProductVariantPriceChange(e, productVariantPrice.title)} value={productVariantPrice.price} className="form-control" type="text"/></td>
                                                        <td><input name="stock" onChange={(e) => onProductVariantPriceChange(e, productVariantPrice.title)} value={productVariantPrice.stock} className="form-control" type="text"/></td>
                                                    </tr>
                                                )
                                            })
                                        }
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <button type="button" onClick={saveProduct} className="btn btn-lg btn-primary">{props.is_for_update == "true" ? "Update" : "Save" }</button>
                <button type="button" className="btn btn-secondary btn-lg">Cancel</button>
            </section>
        </div>
    );
};

export default CreateProduct;
