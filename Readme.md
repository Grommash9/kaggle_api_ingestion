We can see there is a python package create to integrate with Kaggle API.

https://github.com/Kaggle/kagglehub

And it's really covers a lot of requirements we have here

As a responsible developer I do know we should reuse existing code and not reinvent the wheel, to not waste time and effort to getting errors other people already solved.

But there is no any reason to play around with any types or tests with 3rd party libraries, so I have created lib based version in `app/main.py` and it's generating plot using matplotlib.

I don't think there is anything to cover by tests were except really bad categories data merging in.

In `app/main_without_lib.py` I have done my own vision of downloading datasets form Kaggle, we have a check if that dataset exists at all, creating a warning if there is a new version, storing different datasets and versions of them in different gitignored folders, we are checking if file already exists by comparing name and size of it, also checking last modified local and remote dates. 

I don't think there is any real use case for these checks because new version will be released for new file I am assuming. It will overwrite it if download was failed first time or file was modified manually.

In kagglehub library there is a logic for continue downloading file if it was interrupted, it's really interesting, but I have not that much time to play around with it.

Maybe interesting part is tests?

I have used VCR that is library I am really like, it's to create a mocks automatically and reuse that later on, so you don't need to manually create json's store them and load them yourself, I am always trying to use it for integration tests.

For files related tests I am using pytest temp folder functionality.

I have not covered more function and codebase by tests, because I hope it's enough to be able to understand my skills.

I was not sure do you want me to set up CI or not so I have done it.