var mongoose = require('mongoose');
var Schema = mongoose.Schema;

var TuringSchema = new Schema({
  poem: {type: Schema.ObjectId, ref: 'Poem', required: true },
  readability: { type: Number, required: true },
  consistency: { type: Number, required: true },
  poeticness: { type: Number, required: true },
  evocative: { type: Number, required: true },
  overall: { type: Number, required: true },
  author: {type: String, required: true, enum:['Human', 'Computer']}
});

//Export model
module.exports = mongoose.model('Turing', TuringSchema);
