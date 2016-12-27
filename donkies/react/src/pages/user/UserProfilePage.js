import React, {Component, PropTypes} from 'react'
import {
    ChangeEmail,
    ChangePassword,
    EditProfile } from 'components'


export default class UserProfilePage extends Component{
    constructor(props){
        super(props)
    }

    render(){
        return (
            <div className="row">
                <div className="col-lg-4 col-md-6 col-sm-12">
                    <EditProfile />
                </div> 

                <div className="col-lg-4 col-md-6 col-sm-12">
                    <ChangeEmail />
                </div> 

                <div className="col-lg-4 col-md-6 col-sm-12">
                    <ChangePassword />
                </div> 
               
            </div>
        )
    }
}



