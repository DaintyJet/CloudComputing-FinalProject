const fs = require('fs');
const html = fs.readFileSync('index.html', { encoding:'utf8' });

const AWS = require("aws-sdk");
const dynamo = new AWS.DynamoDB.DocumentClient();

var params = {
      TableName: process.env.BucketName,//"gamelist",
//      KeyConditionExpression: "uid = :uid",
//      ExpressionAttributeValues: {
//        ":uid": "albert"
//          }
    };
var table = "";
/**
 * Returns an HTML page containing an interactive Web-based
 * tutorial. Visit the function URL to see it and learn how
 * to build with lambda.
 */
exports.handler = async (event) => {
    console.log (event);
    if(event.queryStringParameters){
        const tablePut = await dynamo.put({
            TableName: process.env.BucketName,
            Item: {
              uid: event.queryStringParameters.name,
              game: event.queryStringParameters.game,
              link: event.queryStringParameters.link
            }
        }).promise();
    }
//    let modifiedHTML = dynamicForm(html,event.queryStringParameters);

//    const tableQuery = await  dynamo.query(params, function(err, data) {
//           if (err) console.log(err);
//           else console.log(data);
//        }).promise() ;   

    let items;
    let link;
    let table = "";
    do {
        
        items = await dynamo.scan(params).promise();
        
        if(items.Items.length>0){
            for (let i = 0; i < items.Items.length; i++) {
             table += "<tr>";
             table += "<td>"+  items.Items[i].uid + "</td>";
             table += "<td>"+  items.Items[i].game + "</td>";
             link = items.Items[i].link;
             table += "<td>" + "<a href=\"" + link + "\" target=\"_blank\"> " + link + "</td>";
             table = table + "</tr> ";
            }
        }

        params.ExclusiveStartKey = items.LastEvaluatedKey;
    } while (typeof items.LastEvaluatedKey != "undefined");
    table += "</table>";
//    callback(null, scanResults);
//    console.log ("table:  ", table);
    
  let  modifiedHTML= html.replace("</table>", table);  
//    html.replace("</table>", table); 
    console.log ("modifiedHTML: ", modifiedHTML);
//    modifiedHTML = dynamictable(modifiedHTML,tableQuery);
    
    const response = {
        statusCode: 200,
        headers: {
            'Content-Type': 'text/html',
        },
        body: modifiedHTML,
    };
    return response;
};

// This does not appear to be used -- Matt
function dynamictable(html,tableQuery){
    let table="<tr>";
        if(tableQuery.Items.length>0){
         for (let i = 0; i < tableQuery.Items.length; i++) {
             table += "<td>"+  tableQuery.Items[i].uid + "</td>";
             table += "<td>"+  tableQuery.Items[i].game + "</td>";
             table += "<td>"+  tableQuery.Items[i].link + "</td>";
 //             table = table+"<td> "+JSON.stringify(tableQuery.Items[i])+"</td>";
            } 
 //          table= "<pre>"+table+"</pre>";
        }
        table = table + "</tr> </table>";
        return html.replace("</table>",table);
}