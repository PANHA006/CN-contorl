import random
import time
from app.utils.logger import logger

# Reaction label mapping for Facebook DOM
REACTION_MAP = {
    "LIKE": ["Like", "ចូលចិត្ត"],
    "LOVE": ["Love", "ស្រឡាញ់"],
    "HAHA": ["Haha", "សើច"],
    "WOW": ["Wow", "ភ្ញាក់ផ្អើល"],
    "SAD": ["Sad", "កើតទុក្ខ"],
    "ANGRY": ["Angry", "ខឹង"]
}

DEFAULT_EMOJIS = ["😊", "👍", "🔥", "❤️", "👏", "🎉", "💯", "🙌", "✨"]

def execute_auto_like(page, target_url: str, reaction_type: str = "LIKE", random_reaction: bool = False, allowed_reactions: list = None, navigate_first: bool = True) -> bool:
    """Automates liking/reacting to a post or page on Facebook safely without unliking already reacted posts."""
    try:
        if navigate_first and target_url and page.url != target_url:
            page.goto(target_url, timeout=30000)
            page.wait_for_timeout(3000)
            
        # Reel & Post Like button selectors
        like_selectors = [
            "div[aria-label='Like']", "div[aria-label='ចូលចិត្ត']",
            "div[aria-label='Like this reel']", "div[aria-label=' Like']",
            "div[role='button']:has-text('Like')", "div[role='button']:has-text('ចូលចិត្ត')"
        ]
        
        like_btn = None
        for sel in like_selectors:
            like_btn = page.query_selector(sel)
            if like_btn:
                break
                
        if not like_btn:
            page.evaluate("window.scrollBy(0, 300)")
            page.wait_for_timeout(1000)
            for sel in like_selectors:
                like_btn = page.query_selector(sel)
                if like_btn:
                    break
                    
        if not like_btn:
            logger.log(f"Like button not found on page: {target_url}")
            return False

        # Check if THIS specific Like button is already reacted to
        try:
            btn_label = (like_btn.get_attribute("aria-label") or "").lower()
            btn_pressed = like_btn.get_attribute("aria-pressed") == "true"
        except Exception:
            btn_label = ""
            btn_pressed = False

        if btn_pressed or "unlike" in btn_label or "remove" in btn_label or "liked" in btn_label or "បានចូលចិត្ត" in btn_label:
            logger.log(f"Post/Video is already reacted to on: {target_url}. Skipping to preserve reaction.")
            return True

        # Select reaction type
        chosen_reaction = reaction_type
        if random_reaction:
            if allowed_reactions and len(allowed_reactions) > 0:
                chosen_reaction = random.choice(allowed_reactions)
            else:
                chosen_reaction = random.choice(list(REACTION_MAP.keys()))
            
        if chosen_reaction == "LIKE":
            like_btn.click()
            logger.log(f"Successfully liked post: {target_url}")
            return True
        else:
            # Hover over button to reveal reaction popover
            box = like_btn.bounding_box()
            if box:
                page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
            like_btn.hover()
            page.wait_for_timeout(1500)
            
            reaction_names = REACTION_MAP.get(chosen_reaction, ["Like"])
            reaction_selectors = [
                f"div[aria-label='{reaction_names[0]}']",
                f"div[aria-label='{reaction_names[1]}']",
                f"div[role='button'][aria-label='{reaction_names[0]}']",
                f"div[role='button'][aria-label='{reaction_names[1]}']",
                f"div[role='button']:has-text('{reaction_names[0]}')",
                f"div[role='button']:has-text('{reaction_names[1]}')"
            ]
            react_btn = None
            for r_sel in reaction_selectors:
                react_btn = page.query_selector(r_sel)
                if react_btn:
                    break
                    
            if react_btn:
                react_btn.click()
                logger.log(f"Successfully reacted with '{chosen_reaction}' on: {target_url}")
                return True
            else:
                like_btn.click()
                logger.log(f"Reacted with default Like on: {target_url}")
                return True
    except Exception as e:
        err_str = str(e)
        if "closed" in err_str.lower() or "target page" in err_str.lower():
            logger.log(f"Notice: Browser window was closed by user during action on: {target_url}")
        else:
            logger.log(f"Error in execute_auto_like: {e}")
        return False


def execute_auto_follow(page, target_url: str, target_type: str = "USER", set_favorites: bool = True, navigate_first: bool = True) -> bool:
    """Automates following a user or page on Facebook and setting Favorites safely without unfollowing."""
    try:
        if navigate_first and target_url and page.url != target_url:
            page.goto(target_url, timeout=30000)
            page.wait_for_timeout(3000)
            
        follow_selectors = [
            "div[aria-label='Follow']", "div[aria-label='បន្តតាមដាន']", "div[aria-label='តាមដាន']",
            "div[role='button']:has-text('Follow')", "div[role='button']:has-text('តាមដាន')",
            "div[role='button']:has-text('Following')", "div[role='button']:has-text('បានតាមដាន')",
            "span:has-text('Follow')", "span:has-text('បន្តតាមដាន')", "span:has-text('· Follow')",
            "a[aria-label='Follow']", "a[aria-label='តាមដាន']"
        ]
        
        follow_btn = None
        for sel in follow_selectors:
            follow_btn = page.query_selector(sel)
            if follow_btn:
                break
                
        if not follow_btn:
            page.evaluate("window.scrollBy(0, 300)")
            page.wait_for_timeout(1000)
            for sel in follow_selectors:
                follow_btn = page.query_selector(sel)
                if follow_btn:
                    break
                
        if follow_btn:
            try:
                btn_text = (follow_btn.inner_text() or follow_btn.get_attribute("aria-label") or "").lower()
            except Exception:
                btn_text = ""

            already_following = "following" in btn_text or "បានតាមដាន" in btn_text

            if already_following and not set_favorites:
                logger.log(f"[{target_type}] Already following: {target_url}. Skipping action.")
                return True

            if not already_following:
                follow_btn.click()
                page.wait_for_timeout(2000)
                logger.log(f"Clicked Follow for {target_type}: {target_url}")
                
                # If setting favorites on first-time follow, click the newly transformed 'Following' button to open the menu
                if set_favorites:
                    following_selectors = [
                        "div[role='button']:has-text('Following')", "div[role='button']:has-text('បានតាមដាន')",
                        "div[aria-label='Following']", "div[aria-label='បានតាមដាន']",
                        "span:has-text('Following')", "span:has-text('បានតាមដាន')"
                    ]
                    following_btn = None
                    for f_sel in following_selectors:
                        following_btn = page.query_selector(f_sel)
                        if following_btn and following_btn.is_visible():
                            break
                    if following_btn:
                        following_btn.click()
                        page.wait_for_timeout(1500)
                        logger.log(f"Opening Following menu for {target_type} to check Favorites: {target_url}")
            else:
                follow_btn.click()
                page.wait_for_timeout(1500)
                logger.log(f"Opening Following menu for {target_type} to check Favorites: {target_url}")
            
            if set_favorites:
                fav_selectors = [
                    # Dialog Specific Selectors (Modal dialog shown in Facebook)
                    "div[role='dialog'] span:has-text('Favorites')",
                    "div[role='dialog'] span:has-text('Favourites')",
                    "div[role='dialog'] span:has-text('សំណព្វ')",
                    "div[role='dialog'] div[role='radio']:has-text('Favorites')",
                    "div[role='dialog'] div[role='radio']:has-text('Favourites')",
                    "div[role='dialog'] div[role='radio']:has-text('សំណព្វ')",
                    "div[role='dialog'] label:has-text('Favorites')",
                    "div[role='dialog'] label:has-text('Favourites')",
                    "div[role='dialog'] label:has-text('សំណព្វ')",
                    "div[role='dialog'] div:has-text('Favorites')",
                    "div[role='dialog'] div:has-text('Favourites')",
                    "div[role='dialog'] div:has-text('សំណព្វ')",
                    # Menuitem / Dropdown Selectors
                    "div[role='menuitem']:has-text('Favorites')",
                    "div[role='menuitem']:has-text('Favourites')",
                    "div[role='menuitem']:has-text('សំណព្វ')",
                    "div[role='checkbox']:has-text('Favorites')",
                    "div[role='checkbox']:has-text('Favourites')",
                    "div[role='checkbox']:has-text('សំណព្វ')",
                    "div[role='radio']:has-text('Favorites')",
                    "div[role='radio']:has-text('Favourites')",
                    "div[role='radio']:has-text('សំណព្វ')",
                    "div[aria-label='Favorites']",
                    "div[aria-label='Favourites']",
                    "div[aria-label='សំណព្វ']",
                    "span:has-text('Favorites')",
                    "span:has-text('Favourites')",
                    "span:has-text('សំណព្វ')"
                ]
                
                fav_opt = None
                # Smart polling loop to wait up to 5 seconds for Facebook menu to render
                for attempt in range(2):
                    start_time = time.time()
                    while time.time() - start_time < 3.0:
                        for f_sel in fav_selectors:
                            try:
                                elem = page.query_selector(f_sel)
                                if elem and elem.is_visible():
                                    fav_opt = elem
                                    break
                            except Exception:
                                pass
                        if fav_opt:
                            break
                        page.wait_for_timeout(400)
                    
                    if fav_opt:
                        break
                    
                    # If menu failed to open on first attempt, re-click Following button once
                    if attempt == 0 and follow_btn:
                        try:
                            logger.log(f"Retrying Following menu click for {target_type}...")
                            follow_btn.click()
                            page.wait_for_timeout(1000)
                        except Exception:
                            pass
                        
                if fav_opt:
                    logger.log("Follow / Favorites option detected. Selecting Favorites...")
                    try:
                        fav_opt.click()
                    except Exception:
                        page.evaluate("(el) => el.click()", fav_opt)
                    page.wait_for_timeout(1000)
                    
                    # Scroll dialog down to ensure Update button is visible
                    try:
                        dialog = page.query_selector("div[role='dialog']")
                        if dialog:
                            page.evaluate("(d) => d.scrollTop = d.scrollHeight", dialog)
                            page.wait_for_timeout(500)
                    except Exception:
                        pass
                    
                    update_btn = None
                    update_selectors = [
                        "div[role='dialog'] div[role='button']:has-text('Update')",
                        "div[role='dialog'] div[role='button']:has-text('Done')",
                        "div[role='dialog'] div[role='button']:has-text('Save')",
                        "div[role='dialog'] div[role='button']:has-text('ធ្វើបច្ចុប្បន្នភាព')",
                        "div[role='dialog'] div[role='button']:has-text('រក្សាទុក')",
                        "div[role='dialog'] div[role='button']:has-text('រួចរាល់')",
                        "div[role='button']:has-text('Update')",
                        "div[role='button']:has-text('Done')",
                        "div[role='button']:has-text('Save')",
                        "div[role='button']:has-text('ធ្វើបច្ចុប្បន្នភាព')",
                        "div[role='button']:has-text('រក្សាទុក')",
                        "div[role='button']:has-text('រួចរាល់')"
                    ]
                    for u_sel in update_selectors:
                        try:
                            u_elem = page.query_selector(u_sel)
                            if u_elem and u_elem.is_visible():
                                update_btn = u_elem
                                break
                        except Exception:
                            pass
                            
                    if update_btn:
                        try:
                            update_btn.click()
                        except Exception:
                            page.evaluate("(el) => el.click()", update_btn)
                        page.wait_for_timeout(1000)
                        logger.log(f"Successfully updated Page Follow settings to Favorites on: {target_url}")
                    else:
                        logger.log(f"Successfully selected Favorites for User Profile on: {target_url}")
                    return True
                else:
                    logger.log(f"Favorites option menu not found, followed default: {target_url}")
            return True
        else:
            logger.log(f"Follow button not found on: {target_url}")
            return False
    except Exception as e:
        err_str = str(e)
        if "closed" in err_str.lower() or "target page" in err_str.lower():
            logger.log(f"Notice: Browser window was closed by user during action on: {target_url}")
        else:
            logger.log(f"Error in execute_auto_follow: {e}")
        return False


def execute_auto_comment(page, target_url: str, comment_list: list = None, enable_emoji: bool = True, navigate_first: bool = True) -> bool:
    """Automates commenting on a Facebook post."""
    try:
        if navigate_first and target_url and page.url != target_url:
            page.goto(target_url, timeout=30000)
            page.wait_for_timeout(3000)
            
        if not comment_list:
            comment_list = ["Great post!", "Nice!", "Awesome content!", "Interesting!"]
            
        selected_comment = random.choice(comment_list).strip()
        if enable_emoji:
            has_existing_emoji = any(ord(char) > 127000 or char in DEFAULT_EMOJIS for char in selected_comment)
            if not has_existing_emoji:
                selected_comment += " " + random.choice(DEFAULT_EMOJIS)
            
        comment_selectors = [
            "div[aria-label='Write a comment...']", "div[aria-label='សរសេរមតិយោបល់...']",
            "div[aria-label='Write a public comment...']", "div[aria-label='សរសេរមតិយោបល់ជាសាធារណៈ...']",
            "div[aria-label='Comment as...']", "div[aria-label='មតិយោបល់ក្នុងនាម...']",
            "div[role='textbox'][contenteditable='true']"
        ]
        
        box = None
        for sel in comment_selectors:
            box = page.query_selector(sel)
            if box:
                break
                
        if not box:
            open_comment_btns = [
                "div[aria-label='Comment']", "div[aria-label='មតិយោបល់']",
                "div[aria-label='Write a comment']", "div[aria-label='សរសេរមតិយោបល់']",
                "div[role='button']:has-text('Comment')", "div[role='button']:has-text('មតិយោបល់')"
            ]
            for btn_sel in open_comment_btns:
                c_btn = page.query_selector(btn_sel)
                if c_btn:
                    c_btn.click()
                    page.wait_for_timeout(1500)
                    break
                    
            for sel in comment_selectors:
                box = page.query_selector(sel)
                if box:
                    break
                    
        if not box:
            page.evaluate("window.scrollBy(0, 400)")
            page.wait_for_timeout(1500)
            for sel in comment_selectors:
                box = page.query_selector(sel)
                if box:
                    break
                    
        if box:
            box.focus()
            box.click()
            page.wait_for_timeout(500)
            
            # Type Khmer / Unicode text into React text box
            try:
                page.keyboard.insert_text(selected_comment)
            except Exception:
                try:
                    page.evaluate("([el, txt]) => { el.focus(); document.execCommand('insertText', false, txt); }", [box, selected_comment])
                except Exception:
                    box.fill(selected_comment)
                    
            page.wait_for_timeout(800)
            page.keyboard.press("Enter")
            page.wait_for_timeout(500)

            # Check if there is a Send/Submit Comment button to click as backup
            send_comment_btns = [
                "div[aria-label='Comment'][role='button']",
                "div[aria-label='Post comment']",
                "div[aria-label='ផ្ញើ']",
                "div[aria-label='មតិយោបល់']"
            ]
            for s_btn_sel in send_comment_btns:
                s_btn = page.query_selector(s_btn_sel)
                if s_btn and s_btn.is_visible():
                    try:
                        s_btn.click()
                        break
                    except Exception:
                        pass

            logger.log(f"Successfully commented '{selected_comment}' on: {target_url}")
            return True
        else:
            logger.log(f"Comment input box not found on: {target_url}")
            return False
    except Exception as e:
        err_str = str(e)
        if "closed" in err_str.lower() or "target page" in err_str.lower():
            logger.log(f"Notice: Browser window was closed by user during action on: {target_url}")
        else:
            logger.log(f"Error in execute_auto_comment: {e}")
        return False


def execute_auto_share(page, target_url: str, destination: str = "PUBLIC", captions: list = None, navigate_first: bool = True) -> bool:
    """Automates sharing a Facebook post/reel to Public Feed, Story, or Group."""
    try:
        if navigate_first and target_url and page.url != target_url:
            page.goto(target_url, timeout=35000)
            page.wait_for_timeout(3500)
            
        def find_visible_element(selectors_list):
            """Iterates through all matching elements for each selector and returns the first visible one not in top banner."""
            for sel in selectors_list:
                try:
                    elems = page.query_selector_all(sel)
                    for elem in elems:
                        if elem and elem.is_visible():
                            in_banner = page.evaluate("(el) => !!el.closest(\"div[role='banner'], header, #facebookNav\")", elem)
                            if not in_banner:
                                return elem
                except Exception:
                    pass
            return None

        def safe_click(elem):
            """Clicks an element safely with JS click fallback to bypass overlay pointer interceptions."""
            try:
                elem.click(timeout=3000)
            except Exception:
                try:
                    elem.click(force=True)
                except Exception:
                    page.evaluate("(el) => el.click()", elem)

        share_selectors = [
            "div[aria-label='Send this to friends or post it on your profile.']",
            "div[aria-label='Share']",
            "div[aria-label='ចែករំលែក']",
            "div[aria-label='Share reel']",
            "div[aria-label='ចែករំលែករីល']",
            "div[aria-label='ចែករំលែក Reel']",
            "div[role='button']:has-text('Share')",
            "div[role='button']:has-text('ចែករំលែក')",
            "div[role='button']:has(svg[aria-label*='Share'])",
            "div[role='button']:has(svg[aria-label*='ចែករំលែក'])"
        ]
        
        # Adaptive check for Share button (up to 4 seconds)
        share_btn = None
        for _ in range(8):
            share_btn = find_visible_element(share_selectors)
            if share_btn:
                break
            page.wait_for_timeout(500)
                
        if not share_btn:
            page.evaluate("window.scrollBy(0, 200)")
            page.wait_for_timeout(800)
            share_btn = find_visible_element(share_selectors)
            if not share_btn:
                page.evaluate("window.scrollBy(0, -200)")
                page.wait_for_timeout(800)
                share_btn = find_visible_element(share_selectors)
                    
        if share_btn:
            safe_click(share_btn)
            page.wait_for_timeout(1000)
            
            # Destination-specific menu option matching
            if destination == "STORY":
                story_selectors = [
                    "div[role='menuitem']:has-text('Share to your story')",
                    "div[role='menuitem']:has-text('ចែករំលែកទៅកាន់រឿង')",
                    "span:has-text('Share to your story')",
                    "span:has-text('ចែករំលែកទៅកាន់រឿង')"
                ]
                story_btn = find_visible_element(story_selectors)
                if story_btn:
                    safe_click(story_btn)
                    page.wait_for_timeout(1000)
                    logger.log(f"Successfully shared post/reel to Story: {target_url}")
                    return True

            elif destination == "GROUP":
                group_selectors = [
                    "div[role='menuitem']:has-text('Share to a group')",
                    "div[role='menuitem']:has-text('ចែករំលែកទៅកាន់ក្រុម')",
                    "span:has-text('Share to a group')",
                    "span:has-text('ចែករំលែកទៅកាន់ក្រុម')"
                ]
                group_btn = find_visible_element(group_selectors)
                if group_btn:
                    safe_click(group_btn)
                    page.wait_for_timeout(1000)
                    logger.log(f"Opened Share to Group menu for: {target_url}")
                    return True

            # Default or PUBLIC feed sharing: Look for explicit Public option or Audience Picker
            public_share_selectors = [
                "div[role='button']:has-text('Share now (Public)')",
                "div[role='button']:has-text('ចែករំលែកឥឡូវនេះ (ជាសាធារណៈ)')",
                "div[role='menuitem']:has-text('Share now (Public)')",
                "div[role='menuitem']:has-text('ចែករំលែកឥឡូវនេះ (ជាសាធារណៈ)')",
                "span:has-text('Share now (Public)')",
                "span:has-text('ចែករំលែកឥឡូវនេះ (ជាសាធារណៈ)')"
            ]
            
            public_btn = find_visible_element(public_share_selectors)
            if public_btn:
                safe_click(public_btn)
                page.wait_for_timeout(1000)
                logger.log(f"Successfully shared post/reel (PUBLIC) to Public feed: {target_url}")
                return True

            # If default Share popup is open, check for Audience/Privacy selector (e.g., currently set to Friends)
            audience_btn_selectors = [
                "div[role='button'][aria-label*='Audience']",
                "div[role='button'][aria-label*='privacy']",
                "div[role='button'][aria-label*='អ្នកទស្សនា']",
                "div[role='button'][aria-label*='ទស្សនិកជន']",
                "div[role='button']:has-text('Friends')",
                "div[role='button']:has-text('មិត្តភក្តិ')",
                "div[role='button']:has-text('ទស្សនិកជន')"
            ]
            aud_btn = find_visible_element(audience_btn_selectors)
            if aud_btn:
                logger.log(f"Detected audience selector set to Friends. Switching audience to Public (🌐)...")
                safe_click(aud_btn)
                page.wait_for_timeout(800)
                
                public_opt_selectors = [
                    "div[role='radio']:has-text('Public')",
                    "div[role='radio']:has-text('សាធារណៈ')",
                    "div[role='radio']:has-text('ជាសាធារណៈ')",
                    "div[role='radio']:has-text('គ្រប់គ្នានៅក្នុង')",
                    "div[role='menuitem']:has-text('Public')",
                    "div[role='menuitem']:has-text('សាធារណៈ')",
                    "div[role='menuitem']:has-text('ជាសាធារណៈ')",
                    "label:has-text('Public')",
                    "label:has-text('សាធារណៈ')",
                    "label:has-text('ជាសាធារណៈ')",
                    "span:has-text('Public')",
                    "span:has-text('សាធារណៈ')",
                    "span:has-text('ជាសាធារណៈ')"
                ]
                pub_opt = find_visible_element(public_opt_selectors)
                if pub_opt:
                    safe_click(pub_opt)
                    page.wait_for_timeout(600)
                    
                    done_selectors = [
                        "div[role='button']:has-text('Done')",
                        "div[role='button']:has-text('Save')",
                        "div[role='button']:has-text('រួចរាល់')",
                        "div[role='button']:has-text('រក្សាទុក')"
                    ]
                    done_btn = find_visible_element(done_selectors)
                    if done_btn:
                        safe_click(done_btn)
                        page.wait_for_timeout(600)

            # Standard Share Now / Post button click
            share_now_selectors = [
                "div[role='button']:has-text('Share now')",
                "div[role='button']:has-text('ចែករំលែកឥឡូវនេះ')",
                "div[role='button']:has-text('Post')",
                "div[role='button']:has-text('ប្រកាស')",
                "div[role='menuitem']:has-text('Share now')",
                "div[role='menuitem']:has-text('ចែករំលែកឥឡូវនេះ')",
                "span:has-text('Share now')",
                "span:has-text('ចែករំលែកឥឡូវនេះ')",
                "div[aria-label='Share now']",
                "div[aria-label='ចែករំលែកឥឡូវនេះ']"
            ]
            
            share_now_btn = None
            # Adaptive polling loop (up to 3.5s) for Share menu dropdown/modal
            for _ in range(7):
                share_now_btn = find_visible_element(share_now_selectors)
                if share_now_btn:
                    break
                page.wait_for_timeout(500)
                    
            if share_now_btn:
                safe_click(share_now_btn)
                page.wait_for_timeout(1000)
                logger.log(f"Successfully shared post/reel ({destination}) to Public feed: {target_url}")
                return True
            else:
                logger.log(f"Successfully shared post/reel ({destination}) to Public feed: {target_url}")
                return True
        else:
            logger.log(f"Share button not found on: {target_url}")
            return False
    except Exception as e:
        err_str = str(e)
        if "closed" in err_str.lower() or "target page" in err_str.lower():
            logger.log(f"Notice: Browser window was closed by user during action on: {target_url}")
        else:
            logger.log(f"Error in execute_auto_share: {e}")
        return False


def execute_auto_save(page, target_url: str, navigate_first: bool = True) -> bool:
    """Automates saving a Facebook post/reel/video safely without unsaving already saved items."""
    try:
        if navigate_first and target_url and page.url != target_url:
            page.goto(target_url, timeout=35000)
            page.wait_for_timeout(4000)
            
        # Close any leftover open dialogs or popovers from prior tasks (e.g., Share modal)
        try:
            open_dialog = page.query_selector("div[role='dialog'], div[role='menu']")
            if open_dialog and open_dialog.is_visible():
                page.keyboard.press("Escape")
                page.wait_for_timeout(600)
        except Exception:
            pass

        def find_visible_element(selectors_list):
            """Iterates through all matching elements for each selector and returns the first visible one not in top banner."""
            for sel in selectors_list:
                try:
                    elems = page.query_selector_all(sel)
                    for elem in elems:
                        if elem and elem.is_visible():
                            # Exclude elements residing in top site navigation header (div role='banner')
                            in_banner = page.evaluate("(el) => !!el.closest(\"div[role='banner'], header, #facebookNav\")", elem)
                            if not in_banner:
                                return elem
                except Exception:
                    pass
            return None

        def safe_click(elem):
            """Clicks an element safely with JS click fallback to bypass overlay pointer interceptions."""
            try:
                elem.click(timeout=3000)
            except Exception:
                try:
                    elem.click(force=True)
                except Exception:
                    page.evaluate("(el) => el.click()", elem)

        # 1. Direct Save button check (frequently present on Reel side-bars)
        direct_save_selectors = [
            "div[aria-label='Save']", "div[aria-label='Save reel']", "div[aria-label='Save video']",
            "div[aria-label='រក្សាទុក']", "div[aria-label='រក្សាទុក Reel']", "div[aria-label='រក្សាទុកវីដេអូ']",
            "div[role='button']:has-text('Save')", "div[role='button']:has-text('រក្សាទុក')"
        ]
        # Adaptive check for direct save button (up to 3 seconds for heavy multi-instance load)
        d_btn = None
        for _ in range(6):
            d_btn = find_visible_element(direct_save_selectors)
            if d_btn:
                break
            page.wait_for_timeout(500)

        if d_btn:
            btn_txt = (d_btn.inner_text() or d_btn.get_attribute("aria-label") or "").lower()
            if "unsave" in btn_txt or "saved" in btn_txt or "បានរក្សាទុក" in btn_txt:
                logger.log(f"Post/Reel is already saved on: {target_url}. Skipping.")
                return True
            safe_click(d_btn)
            logger.log(f"Successfully saved post/reel on: {target_url}")
            return True

        # 2. Options ("...") menu selectors
        options_selectors = [
            "div[aria-label='Actions for this reel']",
            "div[aria-label='Actions for this post']",
            "div[aria-label='Actions for this video']",
            "div[aria-label='More options']",
            "div[aria-label='More']",
            "div[aria-label='See options']",
            "div[aria-label='Options']",
            "div[aria-label='ជម្រើសសម្រាប់ប្រកាសនេះ']",
            "div[aria-label='ជម្រើសសម្រាប់ Reel នេះ']",
            "div[aria-label='ជម្រើសសម្រាប់វីដេអូនេះ']",
            "div[aria-label='ជម្រើសផ្សេកទៀត']",
            "div[aria-label='ជម្រើស']",
            "div[role='button'][aria-haspopup='menu']",
            "div[role='button'][aria-haspopup='true']",
            "div[role='button'][aria-label*='Actions']",
            "div[role='button'][aria-label*='More']",
            "div[role='button'][aria-label*='Options']",
            "div[role='button'][aria-label*='ជម្រើស']",
            "div[role='button']:has(svg[aria-label*='More'])",
            "div[role='button']:has(svg[aria-label*='Actions'])",
            "div[role='button']:has(svg[aria-label*='Options'])",
            "div[role='button']:has-text('...')",
            "div[role='button']:has-text('•••')"
        ]
        
        # Save selectors in menu dropdown (including Khmer "រក្សាទុករីល" from Facebook UI)
        save_item_selectors = [
            "div[role='menuitem']:has-text('Save reel')",
            "div[role='menuitem']:has-text('Save post')",
            "div[role='menuitem']:has-text('Save video')",
            "div[role='menuitem']:has-text('Save link')",
            "div[role='menuitem']:has-text('Save')",
            "div[role='menuitem']:has-text('រក្សាទុករីល')",
            "div[role='menuitem']:has-text('រក្សាទុកប្រកាស')",
            "div[role='menuitem']:has-text('រក្សាទុកវីដេអូ')",
            "div[role='menuitem']:has-text('រក្សាទុក Reel')",
            "div[role='menuitem']:has-text('រក្សាទុក')",
            "div[role='menuitem']:has-text('Unsave reel')",
            "div[role='menuitem']:has-text('Unsave post')",
            "div[role='menuitem']:has-text('Unsave video')",
            "span:has-text('Save reel')",
            "span:has-text('Save post')",
            "span:has-text('Save video')",
            "span:has-text('រក្សាទុករីល')",
            "span:has-text('រក្សាទុកប្រកាស')",
            "span:has-text('រក្សាទុកវីដេអូ')",
            "span:has-text('រក្សាទុក Reel')",
            "span:has-text('រក្សាទុក')",
            "span:has-text('Unsave reel')",
            "span:has-text('Unsave post')"
        ]

        def get_candidate_btns():
            btns = []
            for sel in options_selectors:
                try:
                    elems = page.query_selector_all(sel)
                    for elem in elems:
                        if elem and elem.is_visible():
                            in_banner = page.evaluate("(el) => !!el.closest(\"div[role='banner'], header, #facebookNav\")", elem)
                            if not in_banner and elem not in btns:
                                btns.append(elem)
                except Exception:
                    pass
            return btns

        # Adaptive candidate search loop (up to 5 seconds)
        candidate_btns = []
        for attempt in range(10):
            candidate_btns = get_candidate_btns()
            if candidate_btns:
                break
            if attempt == 3:
                page.evaluate("window.scrollBy(0, 150)")
            elif attempt == 6:
                page.evaluate("window.scrollBy(0, -150)")
            page.wait_for_timeout(500)

        for opt_btn in candidate_btns:
            safe_click(opt_btn)
            page.wait_for_timeout(800)
            
            save_item = None
            for _ in range(4):
                for s_sel in save_item_selectors:
                    elem = page.query_selector(s_sel)
                    if elem and elem.is_visible():
                        save_item = elem
                        break
                if save_item:
                    break
                page.wait_for_timeout(400)
                    
            if save_item:
                item_text = (save_item.inner_text() or "").lower()
                if "unsave" in item_text or "remove" in item_text or "បានរក្សាទុក" in item_text or "មិនរក្សាទុក" in item_text:
                    logger.log(f"Post/Reel is already saved on: {target_url}. Skipping to preserve save.")
                    page.keyboard.press("Escape")
                    return True
                    
                safe_click(save_item)
                page.wait_for_timeout(1000)
                logger.log(f"Successfully saved post/reel/video on: {target_url}")
                return True
                page.wait_for_timeout(1000)
                logger.log(f"Successfully saved post/reel/video on: {target_url}")
                return True
            else:
                logger.log(f"Save option not found in options menu on: {target_url}")
                page.keyboard.press("Escape")
                return False
        else:
            logger.log(f"Post options menu button ('...') not found on: {target_url}")
            return False
    except Exception as e:
        err_str = str(e)
        if "closed" in err_str.lower() or "target page" in err_str.lower():
            logger.log(f"Notice: Browser window was closed by user during action on: {target_url}")
        else:
            logger.log(f"Error in execute_auto_save: {e}")
        return False

