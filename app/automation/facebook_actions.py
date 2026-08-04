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
                page.wait_for_timeout(1500)
                logger.log(f"Clicked Follow for {target_type}: {target_url}")
            else:
                follow_btn.click()
                page.wait_for_timeout(1500)
                logger.log(f"Opening Following menu for {target_type} to check Favorites: {target_url}")
            
            if set_favorites:
                fav_selectors = [
                    "div[role='menuitem']:has-text('Favorites')",
                    "div[role='menuitem']:has-text('ការចូលចិត្ត')",
                    "div[role='checkbox']:has-text('Favorites')",
                    "div[role='dialog'] span:has-text('Favorites')",
                    "div[role='dialog'] span:has-text('ការចូលចិត្ត')",
                    "span:has-text('Favorites')",
                    "span:has-text('ការចូលចិត្ត')",
                    "div:has-text('Favorites')"
                ]
                
                fav_opt = None
                for f_sel in fav_selectors:
                    fav_opt = page.query_selector(f_sel)
                    if fav_opt:
                        break
                        
                if fav_opt:
                    logger.log("Follow / Favorites option detected. Selecting Favorites...")
                    fav_opt.click()
                    page.wait_for_timeout(1000)
                    
                    update_btn = page.query_selector("div[role='button']:has-text('Update'), div[role='button']:has-text('ធ្វើបច្ចុប្បន្នភាព'), div[role='button']:has-text('រក្សាទុក')")
                    if update_btn:
                        update_btn.click()
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
    """Automates sharing a Facebook post to Public Feed, Story, or Group."""
    try:
        if navigate_first and target_url and page.url != target_url:
            page.goto(target_url, timeout=30000)
            page.wait_for_timeout(3000)
            
        share_selectors = [
            "div[aria-label='Send this to friends or post it on your profile.']",
            "div[aria-label='Share']", "div[aria-label='ចែករំលែក']",
            "div[role='button']:has-text('Share')"
        ]
        
        share_btn = None
        for sel in share_selectors:
            share_btn = page.query_selector(sel)
            if share_btn:
                break
                
        if not share_btn:
            page.evaluate("window.scrollBy(0, 300)")
            page.wait_for_timeout(1000)
            for sel in share_selectors:
                share_btn = page.query_selector(sel)
                if share_btn:
                    break
                    
        if share_btn:
            share_btn.click()
            page.wait_for_timeout(1500)
            
            # Destination-specific menu option matching
            if destination == "STORY":
                story_selectors = [
                    "div[role='menuitem']:has-text('Share to your story')",
                    "div[role='menuitem']:has-text('ចែករំលែកទៅកាន់រឿង')",
                    "span:has-text('Share to your story')",
                    "span:has-text('ចែករំលែកទៅកាន់រឿង')"
                ]
                story_btn = None
                for st_sel in story_selectors:
                    story_btn = page.query_selector(st_sel)
                    if story_btn:
                        break
                if story_btn:
                    story_btn.click()
                    page.wait_for_timeout(1000)
                    logger.log(f"Successfully shared post to Story: {target_url}")
                    return True

            elif destination == "GROUP":
                group_selectors = [
                    "div[role='menuitem']:has-text('Share to a group')",
                    "div[role='menuitem']:has-text('ចែករំលែកទៅកាន់ក្រុម')",
                    "span:has-text('Share to a group')",
                    "span:has-text('ចែករំលែកទៅកាន់ក្រុម')"
                ]
                group_btn = None
                for gr_sel in group_selectors:
                    group_btn = page.query_selector(gr_sel)
                    if group_btn:
                        break
                if group_btn:
                    group_btn.click()
                    page.wait_for_timeout(1000)
                    logger.log(f"Opened Share to Group menu for: {target_url}")
                    return True

            # Default or PUBLIC feed sharing: Look for Share Now
            share_now_selectors = [
                "div[role='button']:has-text('Share now')",
                "div[role='button']:has-text('ចែករំលែកឥឡូវនេះ')",
                "span:has-text('Share now')",
                "span:has-text('ចែករំលែកឥឡូវនេះ')",
                "div[aria-label='Share now']",
                "div[aria-label='ចែករំលែកឥឡូវនេះ']"
            ]
            share_now_btn = None
            for sn_sel in share_now_selectors:
                share_now_btn = page.query_selector(sn_sel)
                if share_now_btn:
                    break
                    
            if share_now_btn:
                share_now_btn.click()
                logger.log(f"Successfully shared post ({destination}) to feed: {target_url}")
                return True
            else:
                logger.log(f"Successfully shared post ({destination}) to feed: {target_url}")
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
