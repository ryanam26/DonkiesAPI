

/**
 * Growl notifications: uses bootstrap library
 * http://bootstrap-notify.remabledesigns.com/
 * https://github.com/mouse0270/bootstrap-notify
 * 
 * type: info, success, danger, warning, inverse
 * placementFrom: top, bottom
 * placementAlign: left, right, center
 *
 */
export default class Growl{
    /**
     * @param {string} - message
     * @param {object} - settings
     */
    constructor(message, settings){
        this.message = message
        this.settings = settings
    }

    get type(){
        return this.settings.type || 'inverse'
    }

    get placementFrom(){
        return this.settings.placementFrom || 'top'
    }

    get placementAlign(){
        return this.settings.placementAlign || 'center'
    }

    get delay(){
        return this.settings.delay || 5000
    }

    get offset(){
        return this.settings.offset || 100
    }

    run(){
        $.growl({message: this.message}, {
            type: this.type,
            'placement': {
                from: this.placementFrom,    
                align: this.placementAlign
            }, 
            'delay': this.delay,
            offset: this.offset
        })   
    }
}