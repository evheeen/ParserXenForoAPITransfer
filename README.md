# ParserXenForoAPITransfer

	Parser written for XenForo.

There are two options for parsing.
- The first is parsing each threads of the entire node starting from the specified page.
- The second option is parsing all topics from the section according to the newness of the specified page(reversed).
	
The parser also transfers data to another XenForo forum using [XenForo 2.1 REST API](https://xenforo.com/docs/dev/rest-api/). To do this, you need to set the api key, which is checked for validity, enter the thread ID and the ID prefix.
	
Since you need to parse immediately to another forum, the content is formatted for BBcodes and the excess is deleted. To gain access to hidden content, implemented authorization and bypass pop-up ads. 
