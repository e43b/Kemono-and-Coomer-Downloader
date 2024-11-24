# Kemono and Coomer Downloader  [![Views](https://hits.sh/github.com/e43bkmncoomen/hits.svg)](https://github.com/e43b/Kemono-and-Coomer-Downloader/)

###### [![](img/en-flag.svg) English](README.md) | [![](img/br.png) Português](README-ptbr.md) [![ko-fi](https://www.ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/e43bs)

The **Kemono and Coomer Downloader** is a tool that allows you to download posts from the [Kemono](https://kemono.su/) and [Coomer](https://coomer.su/) websites.

With this tool, you can download single posts, multiple posts sequentially, download all posts from a profile, and download all DMs from a Kemono profile. You can also configure what you want to save in the posts: attachments, videos, create a `.txt` file with information about the post, among others. For more information, visit the [documentation](https://github.com/e43b/Kemono-and-Coomer-Downloader/blob/main/codeen/doc.md).

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=e43b/Kemono-and-Coomer-Downloader&type=Date)](https://star-history.com/#e43b/Kemono-and-Coomer-Downloader&Date)

## How to Use

1. **Make sure you have Python installed on your system.**
2. **Clone this repository:**

    ```sh
    git clone https://github.com/e43b/Kemono-and-Coomer-Downloader/
    ```

3. **Navigate to the project directory:**

    ```sh
    cd Kemono-and-Coomer-Downloader
    ```

4. **Select the desired language:**

    - The `codeen` folder contains the English version.
    - The `codeen` folder contains the Portuguese version.

5. **Run the main script:**

    ```sh
    python main.py
    ```

6. **Follow the instructions in the menu to choose what you want to download or customize the program.**

## Libraries

The required libraries are: `requests` and `beautifulsoup4`. When running the script for the first time, if the libraries are not installed, you will be prompted to install them. Just type "y" and they will be installed automatically.

![Requirements](img/bibliotecas.png)

## Features

### Home Page

The project homepage presents the main options available to facilitate the use of the tool.

![Página Inicial](img/home.png)

### Download Post

#### Option 1: Download posts manually

To download specific posts, simply enter the post links separated by commas. This option is ideal for downloading a few posts. Example:

```sh
https://kemono.su/patreon/user/133054/post/82477856, https://coomer.su/fansly/user/285310079517863936/post/614339200069672960, https://coomer.su/fansly/user/285310079517863936/post/611301068940255234
```

![Posts](img/posts.png)

#### Option 2: Download posts from a JSON file

For those who want to download dozens or more posts from a profile at once, we have a robust alternative:

1. **Generate links from a profile:**

   Navigate to the `codeen` directory and run the command:

   ```sh
   python links.py <profile_url> <parameter>
   ```

   Examples:

   - To extract links of all posts from the profile:

     ```sh
     python links.py https://coomer.su/fansly/user/285310079517863936 all
     ```

   - To extract links of posts from pages 1 to 5:

     ```sh
     python links.py https://coomer.su/fansly/user/285310079517863936 "1 to 5"
     ```

   - To extract links of posts from pages 1, 6, and 9:

     ```sh
     python links.py https://coomer.su/fansly/user/285310079517863936 "1, 6, 9"
     ```

   - To extract links from all available pages, excluding pages 8 to 10 and 25:

     ```sh
     python links.py https://coomer.su/fansly/user/285310079517863936 "-8 to -10, -25"
     ```

   ![img](img/linkextract.png)

2. **Save the links in a JSON file:**

   After running the command, a directory called `links` will be created containing a JSON file. Example: `links/coomer_su_285310079517863936_fansly.json`. This file will have the extracted links.

3. **Download posts using the JSON:**

   Run the main script:

   ```sh
   python main.py
   ```

   Select option 1 to download posts.

   ![img](img/home.png)

   Choose option 1 to download posts from manually added links or option 2 to use the generated JSON file that contains all the links you want to download.

   ![img](img/input.png)

4. **Start the download:**

   Enter the path to the generated JSON file: `links/coomer_su_285310079517863936_fansly.json`.

   The download will start, and all the links available in the JSON file will be downloaded.

   ![img](img/downloadlog.png)
   ![img](img/downloadfile.png)

### Download All Posts from a Profile

To download all posts from a profile, follow these steps:

1. **Select the Download Option**  
   After launching the program, you will be presented with two download options for a profile's posts.

2. **Enter the Profile Link**  
   Input the link of the profile from which you want to download the posts. You will then see the following options:

   ![Options](img/options.png)

   - **Option 1: Download All Posts**  
     To download all available posts from the profile, type "1" and press Enter. The download of all posts will begin automatically.

     ![AllPosts](img/allposts.png)

   - **Option 2: Download Specific Posts**  
     If you want to download only certain specific posts, choose option "2". Here, you need to enter the link of the most recent post and the link of the oldest post you want to download.

     - **Tip:**  
       If you enter "0" in the start post field, the download will begin from the most recent post. Similarly, entering "0" in the end post field will download up to the oldest post available on the profile. You can also use "0" in both fields to download all posts from the profile.  
       **Note:** If you prefer, you can directly enter the post ID, which corresponds to the numbers at the end of the link. For example, in the link "https://kemono.su/patreon/user/17913091/post/107229475," the post ID is "107229475." In the link "https://coomer.su/onlyfans/user/thetinyfeettreatvip/post/855923938," the post ID is "855923938."

     ![SomePosts](img/someposts.png)

### Download DMs

This only works for profiles on the Kemono website, as Coomer does not have this feature. Just put the profile link, and all DMs will be extracted in `.txt` format and saved in the `dm` folder.

![DM](img/dm.png)
![DM arquivos](img/dmarchives.png)

## File Organization

Posts are saved in folders for easier organization. The folder structure is as follows:

1. **Platform:** A main folder is created for the platform (Kemono or Coomer).
2. **Author:** Inside the platform folder, a folder is created for each author.
3. **Posts:** Inside the author's folder, there is a `posts` folder where posts are saved. Each post is saved in a subfolder identified by the post ID.
4. **DMs:** Inside the author's folder, there is also a `DMs` folder where the `.txt` DM files are saved.

Example of the folder structure:

```
Kemono-and-Coomer-Downloader/
│
├── kemono/                               # Kemono platform folder
│   ├── author1/                          # Author 1 folder
│   │   ├── posts/                        # Posts folder for author 1
│   │   │   ├── postID1/                  # Post folder with ID 1
│   │   │   │   ├── post_content          # Post content
│   │   │   │   └── ...                   # Other post files
│   │   │   └── postID2/                  # Post folder with ID 2
│   │   │       ├── post_content          # Post content
│   │   │       └── ...                   # Other post files
│   │   └── DMs/                          # DMs folder for author 1
│   │       ├── dm1.txt                   # DM 1
│   │       ├── dm2.txt                   # DM 2
│   │       └── ...                       # Other DMs
│   └── author2/                          # Author 2 folder
│       ├── posts/                        # Posts folder for author 2
│       └── DMs/                          # DMs folder for author 2
│
└── coomer/                               # Coomer platform folder
    ├── author1/                          # Author 1 folder
    │   ├── posts/                        # Posts folder for author 1
    │   └── DMs/                          # DMs folder for author 1 (if applicable)
    └── author2/                          # Author 2 folder
        ├── posts/                        # Posts folder for author 2
        └── DMs/                          # DMs folder for author 2 (if applicable)
```

![Files](img/arquivo.png)

## Configuration

The configuration page allows you to customize the program according to your needs.

![Settings](img/configure.png)

### Post Configuration

In the post configuration mode, the user can set several options, including:

- **Download Attachments:** Choose whether or not to download attachments.
- **Download Videos:** Choose whether to download videos when available.
- **Save Information:** Save information in a `.txt` file, such as title, post date, import date, and content.
- **Save Comments:** Save post comments in the `.txt` file. To save comments, the save information option must be enabled.

![Settings](img/postconfig.png)

### Profile Configuration

In profile configuration mode, the user can set what they want to download from the posts, similar to the post configuration options. The difference is that the user can filter by posts that have or do not have images, choosing one or the other, or both versions.

![Settings](img/configprofile.png)

For more details, refer to the [documentation](https://github.com/e43b/Kemono-and-Coomer-Downloader/blob/main/codeen/doc.md).

## Contributions

This project is open source, and you are encouraged to contribute improvements and new features. Feel free to send suggestions, report issues, or submit pull requests through the [official GitHub repository](https://github.com/e43b/Kemono-and-Coomer-Downloader/) or through our [Discord](https://discord.gg/TaPhfXawcE).

## Author

Developed and maintained by [E43b](https://github.com/e43b), the Kemono and Coomer Downloader aims to simplify the process of downloading posts from the Kemono and Coomer websites, providing a more accessible and organized experience.

## Support

If you encounter problems, find bugs, or have any questions, visit our [Discord](https://discord.gg/TaPhfXawcE) for help and support.

## Links

- **Project Repository:** [https://github.com/e43b/Kemono-and-Coomer-Downloader/](https://github.com/e43b/Kemono-and-Coomer-Downloader/)
- **Kemono Site:** [https://kemono.su/](https://kemono.su/)
- **Coomer Site:** [https://coomer.su/](https://coomer.su/)


### Support the Project

If you find this tool useful and would like to support its continued development, consider making a donation. Your contribution helps keep the project active and develop new features.

#### Make a donation by accessing [this link](https://oxapay.com/donate/40874860).

---

We hope this tool is useful to you!
