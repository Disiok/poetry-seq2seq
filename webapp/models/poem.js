var mongoose = require('mongoose');
var Schema = mongoose.Schema;

var PoemSchema = new Schema({
  content: {
  	type: String, 
  	default: ''
  },
  keyword: {
    type: String,
    default: ''
  },
  author: {
  	type: String, 
  	required: true, 
  	enum: ['Human', 'Computer']
  },
  model: {
  	type: String, 
    required: true
  }
});

module.exports = mongoose.model('Poem', PoemSchema);